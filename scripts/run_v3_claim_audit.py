from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = Path(r"C:\Users\wangz\OneDrive\Desktop")
SOURCE_MAP = DESKTOP / "PAPER_SOURCE_MAP.md"
FINAL_NAME = "tokenized world model-v3.pdf"
OLD_NAME = "tokenized world model-v2.pdf"
GITHUB_REPO = "Jason-Wang313/tokenized-world-model"
SOURCE_MAP_ROW = f"| `{FINAL_NAME}` | `{ROOT}` | `{GITHUB_REPO}` |"
MIN_PAGES = 25


def fail(message: str) -> None:
    raise SystemExit(f"V3 CLAIM AUDIT FAILED: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def page_count(path: Path) -> int:
    proc = subprocess.run(
        ["pdfinfo", str(path)],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    match = re.search(r"^Pages:\s+(\d+)", proc.stdout, flags=re.MULTILINE)
    if not match:
        fail(f"could not read page count for {path}")
    return int(match.group(1))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def audit_pdfs() -> None:
    repo_pdf = ROOT / "paper" / "final" / FINAL_NAME
    desktop_pdf = DESKTOP / FINAL_NAME
    require(repo_pdf.exists(), f"missing repo final PDF: {repo_pdf}")
    require(desktop_pdf.exists(), f"missing Desktop final PDF: {desktop_pdf}")
    require(page_count(repo_pdf) >= MIN_PAGES, "repo final PDF below 25 pages")
    require(page_count(desktop_pdf) >= MIN_PAGES, "Desktop final PDF below 25 pages")
    require(sha256(repo_pdf) == sha256(desktop_pdf), "repo and Desktop PDF hashes differ")
    require(not (DESKTOP / OLD_NAME).exists(), "old Desktop v2 PDF is still present")


def audit_source_map() -> None:
    require(SOURCE_MAP.exists(), "source map is missing")
    text = read_text(SOURCE_MAP)
    require(SOURCE_MAP_ROW in text, "source map row does not point to v3 final PDF")
    require(OLD_NAME not in text, "source map still references tokenized v2")


def audit_evidence_files() -> None:
    summary_path = ROOT / "results" / "v3_tokenized_evidence_summary.json"
    require(summary_path.exists(), "missing v3 evidence summary")
    summary = json.loads(read_text(summary_path))
    require(summary.get("paper_identity") == "token-likelihood physical aliasing in tokenized/VQ world-model planning", "wrong paper identity")
    require(summary.get("target_page_count_minimum") == MIN_PAGES, "wrong v3 page target")
    require(summary.get("uses_cached_artifacts_only") is True, "v3 summary must say cached artifacts only")
    values = summary.get("key_values", {})
    require(values.get("raw_real_drop", 0) > 0.3, "raw real-utility drop is too small")
    require(values.get("raw_token_gain", 0) > 0.5, "raw token-likelihood gain is too small")
    require(values.get("raw_alias_high_n") == 1.0, "raw high-budget alias rate is not saturated")
    require(values.get("raw_violation_high_n") == 1.0, "raw high-budget violation rate is not saturated")
    require(values.get("combined_gain_high_n", 0) > 0.5, "combined repair gain is too small")
    require(values.get("pilot_gain_high_n", 0) > 0.7, "pilot calibration gain is too small")
    require(values.get("law_mae", 1.0) < 0.01, "finite-law validation MAE is too large")

    for artifact in summary.get("generated_artifacts", []):
        require((ROOT / artifact).exists(), f"listed generated artifact is missing: {artifact}")

    required_tables = [
        ROOT / "paper" / "iclr" / "v3_full_curves_table.tex",
        ROOT / "paper" / "iclr" / "v3_tail_autopsy_table.tex",
        ROOT / "paper" / "iclr" / "v3_codebook_sweep_table.tex",
        ROOT / "paper" / "iclr" / "v3_scorecard_table.tex",
        ROOT / "paper" / "iclr" / "v3_attack_ledger_table.tex",
    ]
    for path in required_tables:
        require(path.exists(), f"missing generated LaTeX table: {path}")


def audit_attack_ledger() -> None:
    ledger_path = ROOT / "results" / "v3_tokenized_attack_ledger.csv"
    require(ledger_path.exists(), "missing v3 attack ledger")
    with ledger_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 50, f"attack ledger has {len(rows)} rows, expected 50")
    statuses = {row.get("status", "") for row in rows}
    require(statuses <= {"pass", "bounded"}, f"unexpected attack statuses: {statuses}")
    angles = {row.get("reviewer_angle", "") for row in rows}
    required_angles = {
        "novelty",
        "scope",
        "overclaim",
        "statistics",
        "mechanism",
        "ablation",
        "calibration",
        "reproducibility",
        "presentation",
        "submission",
        "framing",
        "workflow",
    }
    require(required_angles <= angles, f"attack ledger missing angles: {required_angles - angles}")


def audit_manuscript_text() -> None:
    paper_text = "\n".join(
        [
            read_text(ROOT / "paper" / "iclr" / "main.tex"),
            read_text(ROOT / "paper" / "iclr" / "appendix.tex"),
        ]
    )
    lowered = paper_text.lower()

    duplicate_smells = [
        "best-of",
        "best of",
        "inference value theorem",
        "world action model",
        "wam",
    ]
    for smell in duplicate_smells:
        require(smell not in lowered, f"duplicate-risk phrase remains in manuscript: {smell}")

    positive_overclaims = [
        "we deploy on",
        "we deployed on",
        "hardware experiments show",
        "real-robot experiments show",
        "external benchmark results show",
        "state-of-the-art performance",
        "achieves leaderboard performance",
        "therefore always fixes",
        "therefore always hurts",
        "all tokenized world models fail",
        "guarantees safe deployment",
    ]
    for phrase in positive_overclaims:
        require(phrase not in lowered, f"unsupported positive overclaim remains: {phrase}")

    required_terms = {
        "token": 80,
        "codebook": 15,
        "alias": 25,
        "physical": 25,
        "decode": 15,
        "vq": 5,
        "pilot": 12,
        "finite": 8,
        "utility": 40,
    }
    for term, minimum in required_terms.items():
        count = lowered.count(term)
        require(count >= minimum, f"paper-specific term '{term}' count {count} below {minimum}")

    boundaries = [
        "does not establish hardware deployment",
        "not as a hardware or external-benchmark evaluation",
        "not to claim external benchmark or hardware performance",
        "not hardware deployment evidence",
    ]
    for phrase in boundaries:
        require(phrase in lowered, f"missing boundary language: {phrase}")


def main() -> None:
    audit_pdfs()
    audit_source_map()
    audit_evidence_files()
    audit_attack_ledger()
    audit_manuscript_text()
    print("v3 claim audit passed")


if __name__ == "__main__":
    main()
