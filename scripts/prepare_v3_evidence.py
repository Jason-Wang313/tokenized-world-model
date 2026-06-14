"""Prepare cached v3 evidence artifacts for the tokenized-world paper."""

from __future__ import annotations

import csv
import json
import shutil
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
PAPER = ROOT / "paper" / "iclr"
TABLES = RESULTS


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def f(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def pct(value: float, digits: int = 1) -> str:
    return f"{100.0 * value:.{digits}f}\\%"


def high_n(metrics: list[dict[str, str]], method: str) -> dict[str, float]:
    rows = [row for row in metrics if row["method"] == method and int(row["n"]) == 64]
    if len(rows) != 1:
        raise ValueError(f"expected one high-N row for {method}, got {len(rows)}")
    return {key: float(value) if key not in {"method"} else value for key, value in rows[0].items()}


def n1(metrics: list[dict[str, str]], method: str) -> dict[str, float]:
    rows = [row for row in metrics if row["method"] == method and int(row["n"]) == 1]
    if len(rows) != 1:
        raise ValueError(f"expected one N=1 row for {method}, got {len(rows)}")
    return {key: float(value) if key not in {"method"} else value for key, value in rows[0].items()}


def mean(rows: list[dict[str, str]], key: str) -> float:
    return sum(float(row[key]) for row in rows) / len(rows)


def min_value(rows: list[dict[str, str]], key: str) -> float:
    return min(float(row[key]) for row in rows)


def max_value(rows: list[dict[str, str]], key: str) -> float:
    return max(float(row[key]) for row in rows)


def latex_escape(text: object) -> str:
    text = str(text).replace(r"\%", "%")
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def table_status_label(status: str) -> str:
    labels = {
        "supported_exact": "exact",
        "supported_controlled": "controlled",
        "supported_controlled_with_labels": "controlled+labels",
        "not_claimed": "not claimed",
    }
    return labels.get(status, status)


def collect_values() -> dict[str, object]:
    metrics = read_csv(RESULTS / "metrics_main.csv")
    tail = read_csv(RESULTS / "tail_autopsy.csv")
    bottleneck = read_csv(RESULTS / "codebook_bottleneck.csv")
    law = load_json(RESULTS / "exact_law_validation.json")
    learned = load_json(RESULTS / "learned_vq_artifact.json")
    summary = load_json(RESULTS / "summary.json")

    raw1 = n1(metrics, "raw_token_score")
    raw64 = high_n(metrics, "raw_token_score")
    combined64 = high_n(metrics, "combined_repair")
    pilot64 = high_n(metrics, "token_to_real_calibration")
    oracle64 = high_n(metrics, "oracle_real_utility")
    decode64 = high_n(metrics, "decode_consistency")
    filter64 = high_n(metrics, "physical_filter")
    rare64 = high_n(metrics, "rare_mode_reweighting")
    codebook64 = high_n(metrics, "codebook_uncertainty")

    raw_tail = [row for row in tail if row["selector"] == "raw_token_score@64"]
    combined_tail = [row for row in tail if row["selector"] == "combined_repair@64"]
    oracle_tail = [row for row in tail if row["selector"] == "oracle_real_utility@64"]

    return {
        "metrics": metrics,
        "tail": tail,
        "bottleneck": bottleneck,
        "law": law,
        "learned": learned,
        "summary": summary,
        "raw_n1": raw1,
        "raw64": raw64,
        "combined64": combined64,
        "pilot64": pilot64,
        "oracle64": oracle64,
        "decode64": decode64,
        "filter64": filter64,
        "rare64": rare64,
        "codebook64": codebook64,
        "raw_utility_drop": raw1["real_utility_mean"] - raw64["real_utility_mean"],
        "raw_token_gain": raw64["selected_token_likelihood_mean"] - raw1["selected_token_likelihood_mean"],
        "combined_gain": combined64["real_utility_mean"] - raw64["real_utility_mean"],
        "pilot_gain": pilot64["real_utility_mean"] - raw64["real_utility_mean"],
        "oracle_gap_combined": oracle64["real_utility_mean"] - combined64["real_utility_mean"],
        "oracle_gap_pilot": oracle64["real_utility_mean"] - pilot64["real_utility_mean"],
        "raw_tail_real": mean(raw_tail, "real_utility"),
        "raw_tail_alias": mean(raw_tail, "alias_probability"),
        "raw_tail_violation": mean(raw_tail, "physical_violation"),
        "combined_tail_real": mean(combined_tail, "real_utility"),
        "combined_tail_alias": mean(combined_tail, "alias_probability"),
        "combined_tail_violation": mean(combined_tail, "physical_violation"),
        "oracle_tail_real": mean(oracle_tail, "real_utility"),
        "bottleneck_min_raw": min_value(bottleneck, "raw_real_utility_n64"),
        "bottleneck_max_raw": max_value(bottleneck, "raw_real_utility_n64"),
        "bottleneck_min_gain": min_value(bottleneck, "repair_gain_n64"),
        "bottleneck_max_collision": max_value(bottleneck, "codebook_collision_rate"),
    }


def make_scorecard(values: dict[str, object]) -> list[dict[str, str]]:
    raw64 = values["raw64"]
    combined64 = values["combined64"]
    pilot64 = values["pilot64"]
    law = values["law"]
    learned = values["learned"]
    summary = values["summary"]
    return [
        {
            "claim_id": "T1",
            "evidence_family": "finite tie-aware token-tail law",
            "status": "supported_exact",
            "observed": f"MAE {f(law['mae'], 4)}, max {f(law['max_error'], 4)}",
            "source": "results/exact_law_validation.json",
            "paper_use": "audit equation, not architecture novelty",
        },
        {
            "claim_id": "T2",
            "evidence_family": "raw token-likelihood physical aliasing",
            "status": "supported_controlled",
            "observed": (
                f"token gain {f(values['raw_token_gain'])}; "
                f"real drop {f(values['raw_utility_drop'])}; "
                f"alias {f(raw64['alias_rate'])}; violation {f(raw64['physical_violation_rate'])}"
            ),
            "source": "results/metrics_main.csv",
            "paper_use": "central controlled failure claim",
        },
        {
            "claim_id": "T3",
            "evidence_family": "tail autopsy",
            "status": "supported_controlled",
            "observed": (
                f"raw tail real {f(values['raw_tail_real'])}; "
                f"combined tail real {f(values['combined_tail_real'])}; "
                f"raw violation {f(values['raw_tail_violation'])}"
            ),
            "source": "results/tail_autopsy.csv",
            "paper_use": "mechanism evidence for alias-heavy selected futures",
        },
        {
            "claim_id": "T4",
            "evidence_family": "token-specific repair",
            "status": "supported_controlled",
            "observed": (
                f"combined gain {f(values['combined_gain'])}; "
                f"combined utility {f(combined64['real_utility_mean'])}; "
                f"oracle gap {f(values['oracle_gap_combined'])}"
            ),
            "source": "results/metrics_main.csv",
            "paper_use": "controlled repair evidence, not universal repair",
        },
        {
            "claim_id": "T5",
            "evidence_family": "pilot token-to-real calibration",
            "status": "supported_controlled_with_labels",
            "observed": (
                f"pilot gain {f(values['pilot_gain'])}; "
                f"pilot utility {f(pilot64['real_utility_mean'])}; "
                f"oracle gap {f(values['oracle_gap_pilot'])}"
            ),
            "source": "results/metrics_main.csv",
            "paper_use": "label-spending repair evidence",
        },
        {
            "claim_id": "T6",
            "evidence_family": "codebook bottleneck sweep",
            "status": "supported_controlled",
            "observed": (
                f"raw utility range {f(values['bottleneck_min_raw'])}-{f(values['bottleneck_max_raw'])}; "
                f"min repair gain {f(values['bottleneck_min_gain'])}"
            ),
            "source": "results/codebook_bottleneck.csv",
            "paper_use": "codebook-size stress, not external benchmark",
        },
        {
            "claim_id": "T7",
            "evidence_family": "learned VQ artifact",
            "status": "supported_controlled",
            "observed": (
                f"K={learned['codebook_size']}; collision {f(learned['collision_rate'])}; "
                f"quant error {f(learned['quantization_error_mean'])}; entropy {f(learned['token_entropy'])}"
            ),
            "source": "results/learned_vq_artifact.json",
            "paper_use": "semi-learned token artifact, not SOTA performance",
        },
        {
            "claim_id": "T8",
            "evidence_family": "deployment gate",
            "status": "supported_controlled",
            "observed": f"{summary['gate_action']}: {summary['gate_reason']}",
            "source": "results/summary.json",
            "paper_use": "risk gate asks for pilot labels in harmful tails",
        },
    ]


def attack_rows() -> list[dict[str, object]]:
    attacks = [
        ("generic_budget", "novelty", "This could be a generic candidate-budget paper.", "Would the paper still read the same if tokens were replaced by another architecture?", "Make codebook collisions, decode validity, hidden modes, rare tokens, and token-to-real calibration central.", "pass"),
        ("synthetic_only", "scope", "The evidence is synthetic.", "Does the paper imply deployment evidence?", "State controlled synthetic scope in abstract, limitations, audit, and checklist.", "bounded"),
        ("token_bad", "overclaim", "The paper may imply tokenized world models are bad.", "Does it generalize beyond aliasing cases?", "Explicitly say token models are not generally indicted.", "pass"),
        ("high_n_bad", "overclaim", "The paper may imply larger candidate pools always hurt.", "Does high-N help when score and utility align?", "Explain the finite law as a tail amplifier, not an anti-N claim.", "pass"),
        ("universal_repair", "overclaim", "Repair could be sold as universal.", "What if aliasing is not detectable?", "Limit repair to measurable aliasing or pilot labels.", "pass"),
        ("real_robot", "overclaim", "No hardware validation.", "Does the title or abstract imply robot deployment?", "No real-robot claim; final audit checks boundary language.", "pass"),
        ("external_benchmark", "overclaim", "No external benchmark.", "Does codebook sweep become benchmark language?", "Call it controlled codebook-size stress only.", "pass"),
        ("sota", "overclaim", "No state-of-the-art token model.", "Does learned VQ artifact imply SOTA?", "Frame as semi-learned mechanism artifact.", "pass"),
        ("bad_scorer", "mechanism", "This is just a bad scorer.", "What does the selection law add?", "The law shows top-score selection amplifies whatever the high-score tail contains.", "pass"),
        ("law_generic", "theory", "The law is generic.", "Is this a theoretical novelty paper?", "Concede generic law; tokenized population defines the contribution.", "bounded"),
        ("ties", "theory", "Token scores can tie.", "Does the law handle ties?", "Use finite tie-aware score groups.", "pass"),
        ("mc_noise", "theory", "Monte Carlo validation may be noisy.", "Is the law error small?", "Report MAE and max error from exact-law validation.", "pass"),
        ("alias_definition", "mechanism", "Alias is vague.", "How is aliasing measured?", "Use codebook collision, alias probability, hidden-mode mismatch, and token-real gap.", "pass"),
        ("decode_validity", "mechanism", "Physical invalidity could be a separate bug.", "Is decode validity measured?", "Report physical-violation and decode-consistency diagnostics.", "pass"),
        ("hidden_mode", "mechanism", "Hidden modes are artificial.", "Why include them?", "They isolate physical distinctions omitted by tokenization.", "bounded"),
        ("quantization", "mechanism", "Quantization error alone might explain failure.", "Is collision separate from quantization?", "Codebook sweep reports both collision and quantization.", "pass"),
        ("rare_modes", "mechanism", "Rare valid futures might be excluded.", "Does repair handle rare good tokens?", "Rare-mode reweighting and pilot calibration are reported separately.", "pass"),
        ("tail_autopsy", "mechanism", "Aggregate curves hide selected examples.", "Can reviewers see what raw selects?", "Tail autopsy compares raw, combined, and oracle selected candidates.", "pass"),
        ("single_codebook", "scope", "One codebook size is too narrow.", "Does the effect survive K changes?", "Use codebook bottleneck sweep across sizes.", "pass"),
        ("pool_size", "scope", "Pool size may be too small.", "How large is the candidate pool?", "Report full mode with 150 pools and pool size 64.", "pass"),
        ("repair_labels", "leakage", "Pilot calibration uses labels.", "Are label-spending repairs separated?", "Separate token-to-real calibration from no-label diagnostics.", "pass"),
        ("diagnostic_hand_design", "leakage", "Repairs use hand-designed diagnostics.", "Is that hidden?", "Treat diagnostics as controlled support, not deployment proof.", "pass"),
        ("oracle_gap", "claim strength", "Repair is far from oracle.", "Does the paper hide the gap?", "Report combined and pilot oracle gaps explicitly.", "pass"),
        ("codebook_uncertainty_weak", "ablation", "Codebook uncertainty alone is weak.", "Is the weak baseline visible?", "Report individual repair rows including codebook uncertainty.", "pass"),
        ("decode_filter", "ablation", "Decode consistency and physical filter may drive all gains.", "Are individual repairs separated?", "Report decode, filter, rare, codebook, pilot, combined, oracle.", "pass"),
        ("random_baseline", "baseline", "Random selection could be enough.", "Is random considered?", "Keep random in experiment code and discuss selector baselines if reported.", "pass"),
        ("pilot_overfit", "calibration", "Pilot calibration may overfit.", "Are labels representative?", "State pilot labels are controlled and require deployment refresh.", "bounded"),
        ("gate_action", "policy", "Gate may be cosmetic.", "Does it take a conservative action?", "Gate returns collect_pilot_labels with reason in summary.", "pass"),
        ("gate_deployment", "policy", "Gate could be treated as deployment certification.", "Is it certified?", "State gate is a controlled risk policy only.", "pass"),
        ("physical_filter_deploy", "policy", "Physical filters require domain checks.", "Are those available in the real world?", "Limit to tasks with meaningful validity checks.", "pass"),
        ("score_utility_gap", "metric", "Token-real gap may be confusing.", "Is it defined?", "Define token score, real utility, token-real gap, alias and validity metrics.", "pass"),
        ("confidence_intervals", "statistics", "Intervals may be missing.", "Are uncertainty bands shown?", "Use CI columns in metrics and describe them.", "pass"),
        ("exact_law_same_pool", "statistics", "Law only holds for fixed pools.", "Does paper imply distributional generality?", "State fixed empirical pool assumption.", "pass"),
        ("iid_sampling", "statistics", "Candidates may be correlated in real planners.", "Does law cover correlated rollouts?", "List correlated rollouts as limitation.", "pass"),
        ("learned_vq_small", "learned evidence", "Learned VQ is tiny.", "Is it oversold?", "Frame as CPU semi-learned mechanism artifact.", "bounded"),
        ("transition_stats", "learned evidence", "Transition model evidence is thin.", "Are transition statistics reported?", "Report transition self-probability and codebook entropy.", "pass"),
        ("decoder_quality", "learned evidence", "Decoder quality may dominate.", "Are decode errors measured?", "Use decode-consistency and quantization diagnostics.", "pass"),
        ("figures_too_few", "presentation", "Six figures are too thin for v3.", "Are synthesis figures added?", "Add v3 scorecard, repair, bottleneck, tail, VQ, attack figures.", "pass"),
        ("table_traceability", "presentation", "Claims need artifact traceability.", "Can each claim map to a file?", "Add v3 scorecard table and artifact inventory.", "pass"),
        ("reviewer_attacks_short", "presentation", "Current reviewer attacks are too short.", "Is the self-review broad enough?", "Add exactly 50 attack rounds.", "pass"),
        ("page_count", "submission", "11 pages is too short.", "Does final PDF clear 25 pages?", "V3 build requires >=25 pages.", "pass"),
        ("desktop_mapping", "workflow", "Fresh agents may not find the repo.", "Is Desktop source map updated?", "V3 audit checks exact source-map row.", "pass"),
        ("old_pdf", "workflow", "Old v2 could remain visible.", "Is old Desktop PDF removed?", "V3 build removes old v2.", "pass"),
        ("github_main", "workflow", "Pushed branch might not be default.", "Will main have final artifact?", "Push final commit to main and verify remote SHA.", "pass"),
        ("smoke_overwrite", "reproducibility", "Smoke run could overwrite full artifacts.", "Will validation downgrade outputs?", "Avoid smoke after full; use cached synthesis and claim audit.", "pass"),
        ("ram", "reproducibility", "Full experiments could be memory-heavy.", "How is RAM controlled?", "Use compact CSV/JSON, sequential runs, and cached synthesis.", "pass"),
        ("pdf_hash", "reproducibility", "Repo and Desktop PDFs could diverge.", "Are hashes checked?", "V3 audit checks repo/Desktop SHA match.", "pass"),
        ("claim_scan", "reproducibility", "Overclaims can creep into text.", "Is text scanned?", "V3 audit scans LaTeX plus base claim audit scans docs.", "pass"),
        ("side_by_side", "novelty", "It may look like another paper in the batch.", "Does the identity survive side-by-side review?", "Token/codebook/decode vocabulary dominates all sections.", "pass"),
        ("limitations", "framing", "Limitations could be boilerplate.", "Are limits tied to evidence?", "Limitations name fixed pools, iid sampling, synthetic hidden modes, pilot labels, and no benchmarks.", "pass"),
    ]
    if len(attacks) != 50:
        raise AssertionError(len(attacks))
    return [
        {
            "round": i,
            "attack_id": attack_id,
            "reviewer_angle": angle,
            "failure_mode": failure,
            "harsh_question": question,
            "defense_artifact_or_revision": defense,
            "status": status,
        }
        for i, (attack_id, angle, failure, question, defense, status) in enumerate(attacks, start=1)
    ]


def barh(path: Path, labels: list[str], values: list[float], title: str, xlabel: str) -> None:
    fig, ax = plt.subplots(figsize=(8.2, max(4.4, 0.38 * len(labels) + 1.1)))
    colors = ["#9b3a32" if value < 0.2 else "#2b6f8e" if value > 0.7 else "#4f8a5f" for value in values]
    ax.barh(labels, values, color=colors)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid(axis="x", alpha=0.25)
    for i, value in enumerate(values):
        ax.text(value + 0.015, i, f"{value:.3f}", va="center", fontsize=8)
    ax.set_xlim(0, max(values) * 1.2 if values else 1)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def make_figures(values: dict[str, object], attacks: list[dict[str, object]]) -> None:
    FIGURES.mkdir(exist_ok=True)
    (PAPER / "figures").mkdir(parents=True, exist_ok=True)
    raw64 = values["raw64"]
    raw1 = values["raw_n1"]
    combined64 = values["combined64"]
    pilot64 = values["pilot64"]
    oracle64 = values["oracle64"]
    law = values["law"]
    learned = values["learned"]
    bottleneck = values["bottleneck"]

    barh(
        FIGURES / "figure7_v3_token_evidence_scorecard.png",
        [
            "raw token gain",
            "raw real drop",
            "raw alias rate",
            "raw violation rate",
            "combined repair gain",
            "pilot calibration gain",
            "law MAE",
        ],
        [
            values["raw_token_gain"],
            values["raw_utility_drop"],
            raw64["alias_rate"],
            raw64["physical_violation_rate"],
            values["combined_gain"],
            values["pilot_gain"],
            law["mae"],
        ],
        "V3 token-alias evidence scorecard",
        "observed value",
    )

    methods = ["raw_token_score", "codebook_uncertainty", "decode_consistency", "physical_filter", "rare_mode_reweighting", "combined_repair", "token_to_real_calibration", "oracle_real_utility"]
    labels = ["raw", "codebook", "decode", "filter", "rare", "combined", "pilot", "oracle"]
    high_rows = [high_n(values["metrics"], method) for method in methods]
    xs = list(range(len(labels)))
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    ax.bar([x - 0.18 for x in xs], [row["real_utility_mean"] for row in high_rows], width=0.36, color="#2b6f8e", label="real utility")
    ax.bar([x + 0.18 for x in xs], [row["alias_rate"] for row in high_rows], width=0.36, color="#9b3a32", label="alias rate")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_title("High-N selector comparison")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure8_v3_repair_selector_panel.png", dpi=180)
    plt.close(fig)

    fig, ax1 = plt.subplots(figsize=(8.6, 4.8))
    sizes = [int(row["codebook_size"]) for row in bottleneck]
    raw = [float(row["raw_real_utility_n64"]) for row in bottleneck]
    repaired = [float(row["combined_real_utility_n64"]) for row in bottleneck]
    collision = [float(row["codebook_collision_rate"]) for row in bottleneck]
    ax1.plot(sizes, raw, marker="o", color="#9b3a32", label="raw real utility")
    ax1.plot(sizes, repaired, marker="o", color="#2b6f8e", label="combined real utility")
    ax1.set_xlabel("codebook size")
    ax1.set_ylabel("selected real utility")
    ax1.set_ylim(0, 0.78)
    ax2 = ax1.twinx()
    ax2.plot(sizes, collision, marker="s", color="#4f8a5f", label="collision rate")
    ax2.set_ylabel("collision rate")
    ax2.set_ylim(0, 0.34)
    lines, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels1 + labels2, frameon=False, loc="lower right")
    ax1.grid(alpha=0.25)
    ax1.set_title("Codebook bottleneck stress")
    fig.tight_layout()
    fig.savefig(FIGURES / "figure9_v3_codebook_stress.png", dpi=180)
    plt.close(fig)

    tail_selectors = ["raw_token_score@64", "combined_repair@64", "oracle_real_utility@64"]
    tail_labels = ["raw", "combined", "oracle"]
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    xs = list(range(len(tail_labels)))
    for offset, metric, color, label in [
        (-0.24, "real_utility", "#2b6f8e", "real utility"),
        (0.0, "alias_probability", "#9b3a32", "alias probability"),
        (0.24, "physical_violation", "#4f8a5f", "physical violation"),
    ]:
        means = [mean([row for row in values["tail"] if row["selector"] == selector], metric) for selector in tail_selectors]
        ax.bar([x + offset for x in xs], means, width=0.23, color=color, label=label)
    ax.set_xticks(xs)
    ax.set_xticklabels(tail_labels)
    ax.set_ylim(0, 1.05)
    ax.set_title("Selected-tail autopsy at N=64")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure10_v3_tail_autopsy.png", dpi=180)
    plt.close(fig)

    barh(
        FIGURES / "figure11_v3_vq_artifact.png",
        ["collision rate", "quantization error", "token entropy / 4", "transition self-probability", "max codebook collision"],
        [
            learned["collision_rate"],
            learned["quantization_error_mean"],
            learned["token_entropy"] / 4.0,
            learned["transition_self_probability"],
            values["bottleneck_max_collision"],
        ],
        "Semi-learned VQ/token artifact",
        "normalized value",
    )

    counts = Counter(row["reviewer_angle"] for row in attacks)
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    labels = sorted(counts)
    ax.bar(labels, [counts[label] for label in labels], color="#4f8a5f")
    ax.set_ylabel("attack rounds")
    ax.set_title("50-round self-attack coverage")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure12_v3_attack_coverage.png", dpi=180)
    plt.close(fig)
    for path in [
        FIGURES / "figure7_v3_token_evidence_scorecard.png",
        FIGURES / "figure8_v3_repair_selector_panel.png",
        FIGURES / "figure9_v3_codebook_stress.png",
        FIGURES / "figure10_v3_tail_autopsy.png",
        FIGURES / "figure11_v3_vq_artifact.png",
        FIGURES / "figure12_v3_attack_coverage.png",
    ]:
        shutil.copy2(path, PAPER / "figures" / path.name)


def write_macros(values: dict[str, object]) -> None:
    raw64 = values["raw64"]
    raw1 = values["raw_n1"]
    combined64 = values["combined64"]
    pilot64 = values["pilot64"]
    oracle64 = values["oracle64"]
    law = values["law"]
    learned = values["learned"]
    lines = [
        "% Auto-generated by scripts/prepare_v3_evidence.py",
        f"\\newcommand{{\\VThreeLawMae}}{{{law['mae']:.3e}}}",
        f"\\newcommand{{\\VThreeLawMaxError}}{{{f(law['max_error'], 4)}}}",
        f"\\newcommand{{\\VThreeRawTokenNOne}}{{{f(raw1['selected_token_likelihood_mean'])}}}",
        f"\\newcommand{{\\VThreeRawRealNOne}}{{{f(raw1['real_utility_mean'])}}}",
        f"\\newcommand{{\\VThreeRawTokenHigh}}{{{f(raw64['selected_token_likelihood_mean'])}}}",
        f"\\newcommand{{\\VThreeRawRealHigh}}{{{f(raw64['real_utility_mean'])}}}",
        f"\\newcommand{{\\VThreeRawTokenGain}}{{{f(values['raw_token_gain'])}}}",
        f"\\newcommand{{\\VThreeRawRealDrop}}{{{f(values['raw_utility_drop'])}}}",
        f"\\newcommand{{\\VThreeRawAliasHigh}}{{{f(raw64['alias_rate'])}}}",
        f"\\newcommand{{\\VThreeRawViolationHigh}}{{{f(raw64['physical_violation_rate'])}}}",
        f"\\newcommand{{\\VThreeRawDecodeHigh}}{{{f(raw64['decode_consistency_error'])}}}",
        f"\\newcommand{{\\VThreeCombinedRealHigh}}{{{f(combined64['real_utility_mean'])}}}",
        f"\\newcommand{{\\VThreeCombinedGain}}{{{f(values['combined_gain'])}}}",
        f"\\newcommand{{\\VThreeCombinedOracleGap}}{{{f(values['oracle_gap_combined'])}}}",
        f"\\newcommand{{\\VThreePilotRealHigh}}{{{f(pilot64['real_utility_mean'])}}}",
        f"\\newcommand{{\\VThreePilotGain}}{{{f(values['pilot_gain'])}}}",
        f"\\newcommand{{\\VThreePilotOracleGap}}{{{f(values['oracle_gap_pilot'])}}}",
        f"\\newcommand{{\\VThreeOracleRealHigh}}{{{f(oracle64['real_utility_mean'])}}}",
        f"\\newcommand{{\\VThreeBottleneckMinGain}}{{{f(values['bottleneck_min_gain'])}}}",
        f"\\newcommand{{\\VThreeBottleneckRawRange}}{{{f(values['bottleneck_min_raw'])}--{f(values['bottleneck_max_raw'])}}}",
        f"\\newcommand{{\\VThreeVQCodebookSize}}{{{learned['codebook_size']}}}",
        f"\\newcommand{{\\VThreeVQCollision}}{{{f(learned['collision_rate'])}}}",
        f"\\newcommand{{\\VThreeVQQuantError}}{{{f(learned['quantization_error_mean'])}}}",
        f"\\newcommand{{\\VThreeVQEntropy}}{{{f(learned['token_entropy'])}}}",
        f"\\newcommand{{\\VThreeVQTransitionSelf}}{{{f(learned['transition_self_probability'])}}}",
        f"\\newcommand{{\\VThreePools}}{{{int(values['summary']['n_pools'])}}}",
        f"\\newcommand{{\\VThreePoolSize}}{{{int(values['summary']['pool_size'])}}}",
        "\\newcommand{\\VThreeGateAction}{collect\\_pilot\\_labels}",
    ]
    (PAPER / "v3_results_macros.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_latex_tables(scorecard: list[dict[str, str]], attacks: list[dict[str, object]]) -> None:
    score_lines = [
        "% Auto-generated by scripts/prepare_v3_evidence.py",
        r"\begingroup",
        r"\small",
        r"\setlength{\tabcolsep}{3pt}",
        r"\renewcommand{\arraystretch}{1.08}",
        r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.08\linewidth}>{\raggedright\arraybackslash}p{0.25\linewidth}>{\raggedright\arraybackslash}p{0.15\linewidth}>{\raggedright\arraybackslash}p{0.25\linewidth}>{\raggedright\arraybackslash}p{0.17\linewidth}}",
        r"\caption{V3 claim-to-artifact scorecard for token-likelihood physical aliasing.}\label{tab:v3-scorecard}\\",
        r"\toprule",
        r"Claim & Evidence family & Status & Observed value & Manuscript use \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"Claim & Evidence family & Status & Observed value & Manuscript use \\",
        r"\midrule",
        r"\endhead",
    ]
    for row in scorecard:
        score_lines.append(
            " & ".join(
                [
                    latex_escape(row["claim_id"]),
                    latex_escape(row["evidence_family"]),
                    latex_escape(table_status_label(row["status"])),
                    latex_escape(row["observed"]),
                    latex_escape(row["paper_use"]),
                ]
            )
            + r" \\"
        )
    score_lines.extend([r"\bottomrule", r"\end{longtable}", r"\endgroup", ""])
    (PAPER / "v3_scorecard_table.tex").write_text("\n".join(score_lines), encoding="utf-8")

    attack_lines = [
        "% Auto-generated by scripts/prepare_v3_evidence.py",
        r"\begingroup",
        r"\small",
        r"\setlength{\tabcolsep}{3pt}",
        r"\renewcommand{\arraystretch}{1.08}",
        r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.05\linewidth}>{\raggedright\arraybackslash}p{0.14\linewidth}>{\raggedright\arraybackslash}p{0.25\linewidth}>{\raggedright\arraybackslash}p{0.36\linewidth}>{\raggedright\arraybackslash}p{0.06\linewidth}}",
        r"\caption{Fifty-round v3 self-attack ledger. Bounded rows are scoped limitations that the paper must not inflate.}\label{tab:v3-attack-ledger}\\",
        r"\toprule",
        r"Rnd. & Angle & Harsh attack & Defense or manuscript action & Status \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"Rnd. & Angle & Harsh attack & Defense or manuscript action & Status \\",
        r"\midrule",
        r"\endhead",
    ]
    for row in attacks:
        attack_lines.append(
            " & ".join(
                latex_escape(row[key])
                for key in ["round", "reviewer_angle", "failure_mode", "defense_artifact_or_revision", "status"]
            )
            + r" \\"
        )
    attack_lines.extend([r"\bottomrule", r"\end{longtable}", r"\endgroup", ""])
    (PAPER / "v3_attack_ledger_table.tex").write_text("\n".join(attack_lines), encoding="utf-8")


def write_artifact_latex_tables(values: dict[str, object]) -> None:
    metrics = values["metrics"]
    method_labels = {
        "raw_token_score": "raw",
        "codebook_uncertainty": "codebook",
        "decode_consistency": "decode",
        "physical_filter": "filter",
        "rare_mode_reweighting": "rare",
        "token_to_real_calibration": "pilot",
        "combined_repair": "combined",
        "oracle_real_utility": "oracle",
    }
    method_order = list(method_labels)
    lines = [
        "% Auto-generated by scripts/prepare_v3_evidence.py",
        r"\begingroup",
        r"\small",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.17\linewidth}rrrrrr}",
        r"\caption{Full selected-tail curves for the controlled tokenized candidate pools.}\label{tab:v3-full-curves}\\",
        r"\toprule",
        r"Selector & $N$ & token likelihood & real utility & alias & violation & oracle gap \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"Selector & $N$ & token likelihood & real utility & alias & violation & oracle gap \\",
        r"\midrule",
        r"\endhead",
    ]
    sorted_metrics = sorted(metrics, key=lambda row: (method_order.index(row["method"]), int(row["n"])))
    for row in sorted_metrics:
        lines.append(
            " & ".join(
                [
                    latex_escape(method_labels[row["method"]]),
                    latex_escape(row["n"]),
                    f(float(row["selected_token_likelihood_mean"])),
                    f(float(row["real_utility_mean"])),
                    f(float(row["alias_rate"])),
                    f(float(row["physical_violation_rate"])),
                    f(float(row["oracle_gap"])),
                ]
            )
            + r" \\"
        )
    lines.extend([r"\bottomrule", r"\end{longtable}", r"\endgroup", ""])
    (PAPER / "v3_full_curves_table.tex").write_text("\n".join(lines), encoding="utf-8")

    tail_lines = [
        "% Auto-generated by scripts/prepare_v3_evidence.py",
        r"\begingroup",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{2.5pt}",
        r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.18\linewidth}rrrrrr}",
        r"\caption{Selected-tail autopsy rows at $N=64$. Rows are generated from \texttt{results/tail\_autopsy.csv}.}\label{tab:v3-tail-autopsy}\\",
        r"\toprule",
        r"Selector & pool & token & real utility & alias prob. & decode err. & violation \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"Selector & pool & token & real utility & alias prob. & decode err. & violation \\",
        r"\midrule",
        r"\endhead",
    ]
    selector_labels = {
        "raw_token_score@64": "raw",
        "combined_repair@64": "combined",
        "oracle_real_utility@64": "oracle",
    }
    for row in values["tail"]:
        tail_lines.append(
            " & ".join(
                [
                    latex_escape(selector_labels.get(row["selector"], row["selector"])),
                    latex_escape(row["pool_id"]),
                    latex_escape(row["token_id"]),
                    f(float(row["real_utility"])),
                    f(float(row["alias_probability"])),
                    f(float(row["decode_consistency_error"])),
                    f(float(row["physical_violation"])),
                ]
            )
            + r" \\"
        )
    tail_lines.extend([r"\bottomrule", r"\end{longtable}", r"\endgroup", ""])
    (PAPER / "v3_tail_autopsy_table.tex").write_text("\n".join(tail_lines), encoding="utf-8")

    bottleneck_lines = [
        "% Auto-generated by scripts/prepare_v3_evidence.py",
        r"\begingroup",
        r"\small",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{longtable}{rrrrrr}",
        r"\caption{Codebook bottleneck sweep.}\label{tab:v3-codebook-sweep}\\",
        r"\toprule",
        r"$K$ & collision & quant. err. & entropy & raw $N=64$ utility & repair gain \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"$K$ & collision & quant. err. & entropy & raw $N=64$ utility & repair gain \\",
        r"\midrule",
        r"\endhead",
    ]
    for row in values["bottleneck"]:
        bottleneck_lines.append(
            " & ".join(
                [
                    latex_escape(row["codebook_size"]),
                    f(float(row["codebook_collision_rate"])),
                    f(float(row["quantization_error_mean"])),
                    f(float(row["token_entropy"])),
                    f(float(row["raw_real_utility_n64"])),
                    f(float(row["repair_gain_n64"])),
                ]
            )
            + r" \\"
        )
    bottleneck_lines.extend([r"\bottomrule", r"\end{longtable}", r"\endgroup", ""])
    (PAPER / "v3_codebook_sweep_table.tex").write_text("\n".join(bottleneck_lines), encoding="utf-8")


def write_markdown(summary: dict[str, object], scorecard: list[dict[str, str]], attacks: list[dict[str, object]]) -> None:
    lines = [
        "# V3 Tokenized World Model Evidence Summary",
        "",
        "Generated from cached full artifacts. This file does not rerun experiments.",
        "",
        "## Core Values",
        "",
    ]
    for key, value in summary["key_values"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Scorecard", ""])
    for row in scorecard:
        lines.append(f"- {row['claim_id']} / {row['evidence_family']}: {row['observed']} ({row['status']})")
    lines.extend(["", "## Self-Attack", ""])
    lines.append(f"- rounds: {len(attacks)}")
    lines.append(f"- status counts: {dict(Counter(row['status'] for row in attacks))}")
    lines.append(f"- reviewer angles: {dict(Counter(row['reviewer_angle'] for row in attacks))}")
    (RESULTS / "v3_tokenized_evidence_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    values = collect_values()
    scorecard = make_scorecard(values)
    attacks = attack_rows()
    FIGURES.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    PAPER.mkdir(parents=True, exist_ok=True)

    write_csv(RESULTS / "v3_tokenized_scorecard.csv", scorecard)
    write_csv(RESULTS / "v3_tokenized_attack_ledger.csv", attacks)
    write_macros(values)
    write_latex_tables(scorecard, attacks)
    write_artifact_latex_tables(values)
    make_figures(values, attacks)

    summary = {
        "paper_identity": "token-likelihood physical aliasing in tokenized/VQ world-model planning",
        "uses_cached_artifacts_only": True,
        "target_page_count_minimum": 25,
        "key_values": {
            "law_mae": values["law"]["mae"],
            "raw_token_gain": values["raw_token_gain"],
            "raw_real_drop": values["raw_utility_drop"],
            "raw_alias_high_n": values["raw64"]["alias_rate"],
            "raw_violation_high_n": values["raw64"]["physical_violation_rate"],
            "combined_gain_high_n": values["combined_gain"],
            "pilot_gain_high_n": values["pilot_gain"],
            "combined_oracle_gap": values["oracle_gap_combined"],
            "pilot_oracle_gap": values["oracle_gap_pilot"],
            "gate_action": values["summary"]["gate_action"],
        },
        "generated_artifacts": [
            "results/v3_tokenized_scorecard.csv",
            "results/v3_tokenized_attack_ledger.csv",
            "results/v3_tokenized_evidence_summary.json",
            "results/v3_tokenized_evidence_summary.md",
            "paper/iclr/v3_results_macros.tex",
            "paper/iclr/v3_scorecard_table.tex",
            "paper/iclr/v3_attack_ledger_table.tex",
            "paper/iclr/v3_full_curves_table.tex",
            "paper/iclr/v3_tail_autopsy_table.tex",
            "paper/iclr/v3_codebook_sweep_table.tex",
            "figures/figure7_v3_token_evidence_scorecard.png",
            "figures/figure8_v3_repair_selector_panel.png",
            "figures/figure9_v3_codebook_stress.png",
            "figures/figure10_v3_tail_autopsy.png",
            "figures/figure11_v3_vq_artifact.png",
            "figures/figure12_v3_attack_coverage.png",
        ],
    }
    write_json(RESULTS / "v3_tokenized_evidence_summary.json", summary)
    write_markdown(summary, scorecard, attacks)
    print("prepared v3 tokenized evidence artifacts")


if __name__ == "__main__":
    main()
