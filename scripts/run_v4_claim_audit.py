from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = Path(r"C:\Users\wangz\OneDrive\Desktop")
SOURCE_MAP = DESKTOP / "PAPER_SOURCE_MAP.md"
FINAL_NAME = "tokenized world model-v4.pdf"
OLD_NAMES = ["tokenized world model-v3.pdf", "tokenized world model-v2.pdf"]
GITHUB_REPO = "Jason-Wang313/tokenized-world-model"
SOURCE_MAP_ROW = f"| `{FINAL_NAME}` | `{ROOT}` | `{GITHUB_REPO}` |"
MIN_PAGES = 25


def fail(message: str) -> None:
    raise SystemExit(f"V4 CLAIM AUDIT FAILED: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


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


def pdf_text(path: Path) -> str:
    proc = subprocess.run(
        ["pdftotext", str(path), "-"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
    )
    return re.sub(r"\s+", " ", proc.stdout.lower())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def audit_pdfs() -> None:
    repo_pdf = ROOT / "paper" / "final" / FINAL_NAME
    desktop_pdf = DESKTOP / FINAL_NAME
    require(repo_pdf.exists(), f"missing repo final PDF: {repo_pdf}")
    require(desktop_pdf.exists(), f"missing Desktop final PDF: {desktop_pdf}")
    require(page_count(repo_pdf) >= MIN_PAGES, "repo final PDF below 25 pages")
    require(page_count(desktop_pdf) >= MIN_PAGES, "Desktop final PDF below 25 pages")
    require(sha256(repo_pdf) == sha256(desktop_pdf), "repo and Desktop PDF hashes differ")
    for old_name in OLD_NAMES:
        require(not (DESKTOP / old_name).exists(), f"old Desktop PDF is still present: {old_name}")

    text = pdf_text(repo_pdf)
    for marker in [
        "token-likelihood physical aliasing",
        "v4 tokenized-world submission scorecard",
        "v4 protocol-freeze gates",
        "iclr-style rubric map",
        "60-round v4 reviewer attack ledger",
        "token-to-real calibration",
        "source firewall",
    ]:
        require(marker in text, f"final PDF missing marker: {marker}")


def audit_manifest() -> None:
    manifest_path = ROOT / "paper" / "final" / "tokenized_world_model_v4_manifest.json"
    repo_pdf = ROOT / "paper" / "final" / FINAL_NAME
    require(manifest_path.exists(), "missing v4 manifest")
    manifest = json.loads(read_text(manifest_path))
    require(manifest.get("final_name") == FINAL_NAME, "manifest final name mismatch")
    require(manifest.get("github_repo") == GITHUB_REPO, "manifest GitHub repo mismatch")
    require(manifest.get("pages") == page_count(repo_pdf), "manifest page count mismatch")
    require(manifest.get("sha256") == sha256(repo_pdf), "manifest SHA mismatch")
    require(manifest.get("source_map_row") == SOURCE_MAP_ROW, "manifest source-map row mismatch")


def audit_source_map() -> None:
    require(SOURCE_MAP.exists(), "source map is missing")
    text = read_text(SOURCE_MAP)
    require(SOURCE_MAP_ROW in text, "source map row does not point to v4 final PDF")
    for old_name in OLD_NAMES:
        require(old_name not in text, f"source map still references old tokenized PDF: {old_name}")


def audit_evidence_files() -> None:
    run([sys.executable, str(ROOT / "experiments" / "v4_cached_evidence.py")])
    summary_path = ROOT / "results" / "v4_cached_evidence_summary.json"
    require(summary_path.exists(), "missing v4 evidence summary")
    summary = json.loads(read_text(summary_path))
    require(summary.get("paper_identity") == "token-likelihood physical aliasing in tokenized world-model planning", "wrong paper identity")
    require(summary.get("version") == "v4", "wrong v4 evidence version")
    require(summary.get("uses_cached_artifacts_only") is True, "v4 summary must say cached artifacts only")
    require(summary.get("target_page_count_minimum") == MIN_PAGES, "wrong v4 page target")
    require(summary.get("submission_scorecard_rows") == 12, "wrong scorecard row count")
    require(summary.get("protocol_gates") == 12, "wrong protocol-gate count")
    require(summary.get("protocol_gates_passed") == 12, "not all protocol gates pass")
    require(summary.get("rubric_axes") == 7, "wrong rubric-axis count")
    require(summary.get("rubric_axes_passed") == 7, "not all rubric axes pass")
    require(summary.get("attack_rounds") == 60, "wrong attack-round count")
    require(summary.get("attack_rounds_passed") == 60, "not all v4 attacks pass")

    for artifact in summary.get("generated_artifacts", []):
        require((ROOT / artifact).exists(), f"listed generated artifact is missing: {artifact}")
    for artifact in [
        "results/v4_cached_evidence_summary.md",
        "results/v4_reviewer_attack_ledger.md",
        "figures/figure13_v4_token_evidence_matrix.png",
        "figures/figure14_v4_protocol_freeze.png",
        "figures/figure15_v4_iclr_rubric.png",
        "figures/figure16_v4_attack_coverage.png",
        "figures/figure17_v4_source_firewall.png",
    ]:
        require((ROOT / artifact).exists(), f"missing v4 artifact: {artifact}")

    scorecard = csv_rows(ROOT / "results" / "v4_tokenized_submission_scorecard.csv")
    protocol = csv_rows(ROOT / "results" / "v4_protocol_freeze_gates.csv")
    rubric = csv_rows(ROOT / "results" / "v4_iclr_style_rubric_map.csv")
    attacks = csv_rows(ROOT / "results" / "v4_reviewer_attack_ledger.csv")
    require(len(scorecard) == 12, "v4 scorecard must have 12 rows")
    require(len(protocol) == 12, "v4 protocol gate table must have 12 rows")
    require(len(rubric) == 7, "v4 rubric table must have 7 rows")
    require(len(attacks) == 60, "v4 reviewer ledger must have 60 rows")
    require(all(row.get("gate") == "PASS" for row in scorecard), "not all scorecard gates pass")
    require(all(row.get("status") == "PASS" for row in protocol), "not all protocol rows pass")
    require(all(row.get("status") == "PASS" for row in rubric), "not all rubric rows pass")
    require(all(row.get("status") == "PASS" for row in attacks), "not all attack rows pass")


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

    required_markers = [
        r"\input{v4_results_macros.tex}",
        r"\input{v4_scorecard_table.tex}",
        r"\input{v4_protocol_gate_table.tex}",
        r"\input{v4_rubric_table.tex}",
        r"\input{v4_attack_ledger_table.tex}",
        "protocol-freeze gates",
        "iclr-style rubric",
        "source firewall",
        "60-round",
    ]
    for marker in required_markers:
        require(marker.lower() in lowered, f"missing v4 manuscript marker: {marker}")

    required_terms = {
        "token": 100,
        "codebook": 20,
        "alias": 35,
        "physical": 30,
        "decode": 20,
        "vq": 6,
        "pilot": 15,
        "finite": 10,
        "utility": 50,
    }
    for term, minimum in required_terms.items():
        count = lowered.count(term)
        require(count >= minimum, f"paper-specific term '{term}' count {count} below {minimum}")

    citation_count = len(re.findall(r"\\cite[t|p]?\{", paper_text))
    require(citation_count >= 8, f"citation surface too thin: {citation_count}")

    boundaries = [
        "does not establish hardware deployment",
        "not as a hardware or external-benchmark evaluation",
        "not to claim external benchmark or hardware performance",
        "not hardware deployment evidence",
        "controlled mechanism audit",
    ]
    for phrase in boundaries:
        require(phrase in lowered, f"missing boundary language: {phrase}")


def audit_docs_text() -> None:
    forbidden = [
        "we solve tokenized world modeling",
        "we solve world-token planning",
        "score-tail always hurts",
        "token models are bad",
        "codebook uncertainty always fixes it",
        "real-robot validation",
        "this is just wam renamed",
        "this is just video transformer prediction",
    ]
    paths = list((ROOT / "docs").glob("*.md")) + list((ROOT / "paper").glob("*.md")) + [ROOT / "README.md"]
    for path in paths:
        text = read_text(path).lower()
        for phrase in forbidden:
            require(phrase not in text, f"{path.relative_to(ROOT)} contains forbidden phrase: {phrase}")


def main() -> None:
    audit_pdfs()
    audit_manifest()
    audit_source_map()
    audit_evidence_files()
    audit_manuscript_text()
    audit_docs_text()
    print("v4 claim audit passed")


if __name__ == "__main__":
    main()
