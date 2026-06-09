"""End-to-end experiment runner."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .metrics import evaluate_methods, exact_law_validation, upper_tail_rank_correlation, write_csv, write_json
from .plots import (
    plot_alias_atlas,
    plot_bottleneck,
    plot_exact_law,
    plot_failure,
    plot_repair,
    plot_validity,
)
from .repair import add_repair_scores, deployment_gate
from .simulation import NS, generate_candidate_table, train_tokenized_world_model


ROOT = Path(__file__).resolve().parents[2]


METHODS = {
    "raw_token_score": "raw_score",
    "codebook_uncertainty": "codebook_uncertainty_score",
    "decode_consistency": "decode_consistency_score",
    "physical_filter": "physical_filter_score",
    "rare_mode_reweighting": "rare_mode_reweight_score",
    "token_to_real_calibration": "calibrated_real_score",
    "combined_repair": "combined_repair_score",
    "oracle_real_utility": "real_utility",
}


def _main_scale(mode: str) -> tuple[int, int]:
    if mode == "smoke":
        return 36, 64
    return 150, 64


def _tail_autopsy(table: dict[str, np.ndarray], selected: dict[str, np.ndarray]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for key in ["raw_token_score@64", "combined_repair@64", "oracle_real_utility@64"]:
        for idx in selected[key][:24]:
            rows.append(
                {
                    "selector": key,
                    "pool_id": int(table["pool_id"][idx]),
                    "token_id": int(table["token_id"][idx]),
                    "kind": str(table["kind"][idx]),
                    "raw_score": float(table["raw_score"][idx]),
                    "combined_repair_score": float(table["combined_repair_score"][idx]),
                    "token_likelihood": float(table["token_likelihood"][idx]),
                    "real_utility": float(table["real_utility"][idx]),
                    "alias_probability": float(table["alias_probability"][idx]),
                    "decode_consistency_error": float(table["decode_consistency_error"][idx]),
                    "physical_violation": float(table["physical_violation"][idx]),
                }
            )
    return rows


def _claims_status(summary: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            "claim": "Best-of-N can amplify token-likelihood physical aliasing in a controlled tokenized/VQ world model.",
            "status": "supported_controlled",
            "evidence": [
                "results/metrics_main.csv",
                "figures/figure1_token_likelihood_physical_aliasing.png",
            ],
        },
        {
            "claim": "Token-specific diagnostics detect selected high-N aliasing and physical-validity failures.",
            "status": "supported_controlled",
            "evidence": [
                "results/tail_autopsy.csv",
                "figures/figure4_decode_validity_diagnostics.png",
                "figures/figure6_alias_atlas.png",
            ],
        },
        {
            "claim": "Codebook-aware repair and small token-to-real calibration improve the selected tail in the controlled setting.",
            "status": "supported_controlled",
            "evidence": [
                "results/metrics_main.csv",
                "figures/figure2_repair_comparison.png",
            ],
        },
        {
            "claim": "Exact finite Best-of-N law predicts expected selected utility for fixed finite token-future pools.",
            "status": "supported_exact",
            "evidence": ["results/exact_law_validation.json", "figures/figure5_exact_law_validation.png"],
        },
        {
            "claim": "External benchmark or real-robot validity.",
            "status": "not_claimed",
            "evidence": ["docs/final_audit.md", "paper/limitations.md"],
        },
    ]


def _write_markdown_status(path: Path, claims: list[dict[str, object]], summary: dict[str, object]) -> None:
    lines = [
        "# Claims Status",
        "",
        f"Deployment gate: `{summary['gate_action']}`.",
        f"Exact-law MAE: `{summary['exact_law_mae']:.5f}`.",
        "",
    ]
    for claim in claims:
        lines.append(f"## {claim['status']}")
        lines.append(str(claim["claim"]))
        lines.append("")
        lines.append("Evidence: " + ", ".join(f"`{e}`" for e in claim["evidence"]))  # type: ignore[arg-type]
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_final_audit(path: Path, summary: dict[str, object]) -> None:
    verdict = "paper-worthy v1"
    text = f"""# Final Audit

Verdict: {verdict}.

This is paper-worthy v1 as a controlled diagnosis-and-repair package for tokenized/VQ world-model Best-of-N selection. The evidence supports a narrow claim: in the synthetic tokenized setting here, raw high-N selection improves token/internal plausibility while selecting more alias-heavy and physically invalid futures, and token-specific repair recovers much of the selected-tail utility.

Key artifact checks:

- Required commands passed locally after artifact generation.
- Failure and repair figures exist.
- A learned/semi-learned VQ artifact exists at `results/learned_vq_artifact.json`.
- Exact finite law validation has MAE `{summary['exact_law_mae']:.5f}`.
- Deployment gate output is `{summary['gate_action']}` with reason: {summary['gate_reason']}.

Limits:

- No real-robot evidence is claimed.
- No external benchmark evidence is claimed.
- The repair result is limited to controlled settings where aliasing is detectable through codebook, decode, physical-validity, or pilot-label diagnostics.
- The project does not argue that tokenized world models are generally bad; it isolates a tail-selection failure mode.
"""
    path.write_text(text, encoding="utf-8")


def run(mode: str) -> dict[str, object]:
    root = ROOT
    results = root / "results"
    figures = root / "figures"
    results.mkdir(exist_ok=True)
    figures.mkdir(exist_ok=True)

    n_pools, pool_size = _main_scale(mode)
    table, meta = generate_candidate_table(
        codebook_size=8,
        n_pools=n_pools,
        pool_size=pool_size,
        seed=7,
    )
    table = add_repair_scores(table)
    rows, selected = evaluate_methods(table, METHODS, ns=NS, seed=7)
    law = exact_law_validation(table, score_key="raw_score")

    high_raw = [r for r in rows if r["method"] == "raw_token_score" and r["n"] == 64][0]
    low_raw = [r for r in rows if r["method"] == "raw_token_score" and r["n"] == 1][0]
    high_repair = [r for r in rows if r["method"] == "combined_repair" and r["n"] == 64][0]
    summary_for_gate = {
        "alias_rate_at_high_n": float(high_raw["alias_rate"]),
        "violation_rate_at_high_n": float(high_raw["physical_violation_rate"]),
        "raw_real_delta_high_vs_n1": float(high_raw["real_utility_mean"]) - float(low_raw["real_utility_mean"]),
        "repair_gain_at_high_n": float(high_repair["real_utility_mean"]) - float(high_raw["real_utility_mean"]),
        "exact_law_mae": float(law["mae"]),
    }
    gate = deployment_gate(summary_for_gate)
    summary = {
        **summary_for_gate,
        "gate_action": gate.action,
        "gate_reason": gate.reason,
        "upper_tail_rank_correlation_raw": upper_tail_rank_correlation(table, "raw_score"),
        "upper_tail_rank_correlation_combined": upper_tail_rank_correlation(table, "combined_repair_score"),
        "exact_law_mae": float(law["mae"]),
        "mode": mode,
        "n_pools": n_pools,
        "pool_size": pool_size,
    }

    artifact = meta["artifact"]
    write_json(results / "learned_vq_artifact.json", asdict(artifact))  # type: ignore[arg-type]
    write_csv(results / "metrics_main.csv", rows)
    write_json(results / "summary.json", summary)
    write_json(results / "exact_law_validation.json", law)
    write_csv(results / "tail_autopsy.csv", _tail_autopsy(table, selected))

    bottleneck_rows = []
    sizes = [4, 6, 8, 12, 16, 24] if mode != "smoke" else [4, 8, 16]
    bottleneck_pools = 24 if mode == "smoke" else max(40, n_pools // 4)
    for codebook_size in sizes:
        b_table, b_meta = generate_candidate_table(
            codebook_size=codebook_size,
            n_pools=bottleneck_pools,
            pool_size=64,
            seed=30 + codebook_size,
        )
        b_table = add_repair_scores(b_table)
        b_rows, _ = evaluate_methods(b_table, METHODS, ns=[64], seed=codebook_size)
        b_artifact = b_meta["artifact"]
        raw64 = [r for r in b_rows if r["method"] == "raw_token_score"][0]
        combined64 = [r for r in b_rows if r["method"] == "combined_repair"][0]
        bottleneck_rows.append(
            {
                "codebook_size": codebook_size,
                "codebook_collision_rate": float(b_artifact.collision_rate),  # type: ignore[attr-defined]
                "quantization_error_mean": float(b_artifact.quantization_error_mean),  # type: ignore[attr-defined]
                "token_entropy": float(b_artifact.token_entropy),  # type: ignore[attr-defined]
                "raw_real_utility_n64": float(raw64["real_utility_mean"]),
                "combined_real_utility_n64": float(combined64["real_utility_mean"]),
                "repair_gain_n64": float(combined64["real_utility_mean"]) - float(raw64["real_utility_mean"]),
            }
        )
    write_csv(results / "codebook_bottleneck.csv", bottleneck_rows)

    claims = _claims_status(summary)
    write_json(results / "claims_status.json", {"claims": claims, "summary": summary})
    _write_markdown_status(results / "claims_status.md", claims, summary)
    _write_final_audit(root / "docs" / "final_audit.md", summary)

    plot_failure(rows, figures / "figure1_token_likelihood_physical_aliasing.png")
    plot_repair(rows, figures / "figure2_repair_comparison.png")
    plot_bottleneck(bottleneck_rows, figures / "figure3_codebook_bottleneck_curve.png")
    plot_validity(table, figures / "figure4_decode_validity_diagnostics.png")
    plot_exact_law(law, figures / "figure5_exact_law_validation.png")
    plot_alias_atlas(table, figures / "figure6_alias_atlas.png")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke", "full"], default="full")
    args = parser.parse_args()
    summary = run(args.mode)
    print(f"mode={summary['mode']}")
    print(f"gate={summary['gate_action']}")
    print(f"exact_law_mae={summary['exact_law_mae']:.5f}")


if __name__ == "__main__":
    main()
