"""Claim and artifact audit."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_PHRASES = [
    "we solve tokenized world modeling",
    "we solve world-token planning",
    "score-tail always hurts",
    "token models are bad",
    "codebook uncertainty always fixes it",
    "real-robot validation",
    "this is just wam renamed",
    "this is just video transformer prediction",
]

REQUIRED_ARTIFACTS = [
    "results/metrics_main.csv",
    "results/claims_status.md",
    "results/claims_status.json",
    "results/exact_law_validation.json",
    "results/learned_vq_artifact.json",
    "docs/final_audit.md",
    "figures/figure1_token_likelihood_physical_aliasing.png",
    "figures/figure2_repair_comparison.png",
    "figures/figure3_codebook_bottleneck_curve.png",
    "figures/figure4_decode_validity_diagnostics.png",
    "figures/figure5_exact_law_validation.png",
]

ALLOWED_VERDICTS = [
    "paper-worthy v1",
    "needs stronger learned model",
    "needs benchmark validation",
    "redesign required",
]


def _scan_text() -> list[str]:
    hits = []
    for path in list((ROOT / "docs").glob("*.md")) + list((ROOT / "paper").glob("*.md")) + [ROOT / "README.md"]:
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in text:
                hits.append(f"{path.relative_to(ROOT)} contains forbidden phrase: {phrase}")
    return hits


def run_audit() -> list[str]:
    failures: list[str] = []
    for rel in REQUIRED_ARTIFACTS:
        path = ROOT / rel
        if not path.exists() or path.stat().st_size == 0:
            failures.append(f"missing or empty artifact: {rel}")

    claims_path = ROOT / "results" / "claims_status.json"
    if claims_path.exists():
        payload = json.loads(claims_path.read_text(encoding="utf-8"))
        claims = payload.get("claims", [])
        if not claims:
            failures.append("claims_status.json has no claims")
        for claim in claims:
            if claim.get("status") not in {"supported_controlled", "supported_exact", "not_claimed"}:
                failures.append(f"invalid claim status: {claim}")
            for evidence in claim.get("evidence", []):
                if not (ROOT / evidence).exists():
                    failures.append(f"claim evidence missing: {evidence}")

    final_audit = ROOT / "docs" / "final_audit.md"
    if final_audit.exists():
        text = final_audit.read_text(encoding="utf-8").lower()
        verdict_hits = [verdict for verdict in ALLOWED_VERDICTS if verdict in text]
        if len(verdict_hits) != 1:
            failures.append(f"final audit must contain exactly one allowed verdict, found {verdict_hits}")

    failures.extend(_scan_text())
    return failures


def main() -> None:
    failures = run_audit()
    if failures:
        print("CLAIM AUDIT FAILED")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CLAIM AUDIT PASSED")


if __name__ == "__main__":
    main()

