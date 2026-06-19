from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "paper" / "iclr"
DESKTOP = Path(r"C:\Users\wangz\OneDrive\Desktop")
SOURCE_MAP = DESKTOP / "PAPER_SOURCE_MAP.md"
FINAL_NAME = "tokenized world model-v4.pdf"
OLD_NAMES = ["tokenized world model-v3.pdf", "tokenized world model-v2.pdf"]
GITHUB_REPO = "Jason-Wang313/tokenized-world-model"
SOURCE_MAP_ROW = f"| `{FINAL_NAME}` | `{ROOT}` | `{GITHUB_REPO}` |"
MIN_PAGES = 25

REQUIRED_PDF_MARKERS = [
    "token-likelihood physical aliasing",
    "v4 tokenized-world submission scorecard",
    "v4 protocol-freeze gates",
    "iclr-style rubric map",
    "60-round v4 reviewer attack ledger",
    "token-to-real calibration",
    "codebook",
    "physical aliasing",
    "source firewall",
]

FORBIDDEN_PDF_PHRASES = [
    "best-of",
    "best of",
    "inference value theorem",
    "world action model",
    "state-of-the-art performance",
    "achieves leaderboard performance",
    "guarantees safe deployment",
    "therefore always fixes",
    "therefore always hurts",
    "all tokenized world models fail",
    "hardware experiments show",
    "external benchmark results show",
]


def run(cmd: list[str], cwd: Path = ROOT, allow_nonzero: bool = False) -> subprocess.CompletedProcess:
    print("+ " + " ".join(cmd))
    proc = subprocess.run(cmd, cwd=cwd)
    if proc.returncode and not allow_nonzero:
        raise subprocess.CalledProcessError(proc.returncode, cmd)
    if proc.returncode and allow_nonzero:
        print(f"warning: tolerated exit {proc.returncode} from {' '.join(cmd)}")
    return proc


def git_output(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.stdout.strip()


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
        raise RuntimeError(f"could not read page count for {path}")
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


def update_source_map() -> None:
    if SOURCE_MAP.exists():
        text = SOURCE_MAP.read_text(encoding="utf-8")
    else:
        text = "\n".join(
            [
                "# Desktop Paper Source Map",
                "",
                "| Latest/target Desktop PDF | Source folder | GitHub repo |",
                "|---|---|---|",
            ]
        ) + "\n"
    if "## V4 Verification Ledger" in text:
        lookup_text, ledger_text = text.split("## V4 Verification Ledger", 1)
        ledger_text = "## V4 Verification Ledger" + ledger_text
    else:
        lookup_text, ledger_text = text, ""
    lines = lookup_text.splitlines()
    replaced = False
    for idx, line in enumerate(lines):
        parts = [part.strip() for part in line.split("|")]
        is_lookup_row = len(parts) == 5 and (FINAL_NAME in line or GITHUB_REPO in line or str(ROOT) in line)
        if is_lookup_row:
            lines[idx] = SOURCE_MAP_ROW
            replaced = True
    if not replaced:
        lines.append(SOURCE_MAP_ROW)
    updated = "\n".join(lines).rstrip() + "\n"
    if ledger_text:
        updated += "\n" + ledger_text.rstrip() + "\n"
    SOURCE_MAP.write_text(updated, encoding="utf-8")


def audit_pdf_text(path: Path) -> None:
    text = pdf_text(path)
    missing = [marker for marker in REQUIRED_PDF_MARKERS if marker not in text]
    if missing:
        raise RuntimeError(f"final PDF is missing expected markers: {missing}")
    forbidden = [phrase for phrase in FORBIDDEN_PDF_PHRASES if phrase in text]
    if forbidden:
        raise RuntimeError(f"final PDF contains unsupported or duplicate-risk phrases: {forbidden}")


def main() -> None:
    run([sys.executable, str(ROOT / "experiments" / "v4_cached_evidence.py")])
    run(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(PAPER_DIR / "build.ps1"),
        ],
        allow_nonzero=True,
    )

    compiled_pdf = PAPER_DIR / "main.pdf"
    if not compiled_pdf.exists() or compiled_pdf.stat().st_size <= 0:
        raise RuntimeError("LaTeX build did not produce a non-empty main.pdf")

    pages = page_count(compiled_pdf)
    if pages < MIN_PAGES:
        raise RuntimeError(f"final PDF has {pages} pages, below {MIN_PAGES}")
    audit_pdf_text(compiled_pdf)

    final_dir = ROOT / "paper" / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    repo_final_pdf = final_dir / FINAL_NAME
    desktop_final_pdf = DESKTOP / FINAL_NAME
    shutil.copy2(compiled_pdf, repo_final_pdf)
    shutil.copy2(compiled_pdf, desktop_final_pdf)

    for old_name in OLD_NAMES:
        old_desktop_pdf = DESKTOP / old_name
        if old_desktop_pdf.exists():
            old_desktop_pdf.unlink()

    update_source_map()

    pdf_hash = sha256(repo_final_pdf)
    if sha256(desktop_final_pdf) != pdf_hash:
        raise RuntimeError("repo final PDF and Desktop PDF hashes differ")

    manifest = {
        "final_name": FINAL_NAME,
        "pages": pages,
        "sha256": pdf_hash,
        "source_folder": str(ROOT),
        "repo_pdf": str(repo_final_pdf),
        "desktop_pdf": str(desktop_final_pdf),
        "source_map": str(SOURCE_MAP),
        "source_map_row": SOURCE_MAP_ROW,
        "github_repo": GITHUB_REPO,
        "github_remote": git_output(["remote", "get-url", "origin"]),
        "git_branch_at_build": git_output(["branch", "--show-current"]),
        "old_desktop_pdfs_removed": OLD_NAMES,
        "required_pdf_markers": REQUIRED_PDF_MARKERS,
        "verification_scope": [
            "cached v4 evidence synthesis",
            "LaTeX final PDF build",
            "repo/Desktop PDF SHA-256 equality",
            "minimum page-count gate",
            "required v4 PDF text markers",
            "forbidden duplicate/overclaim phrase scan",
            "old visible Desktop versions removed",
            "Desktop source-map lookup row updated without touching the verification ledger",
        ],
        "verified_on": dt.date.today().isoformat(),
        "built_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    manifest_path = final_dir / "tokenized_world_model_v4_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"finalized {FINAL_NAME}")
    print(f"pages: {pages}")
    print(f"sha256: {pdf_hash}")
    print(f"repo pdf: {repo_final_pdf}")
    print(f"desktop pdf: {desktop_final_pdf}")


if __name__ == "__main__":
    main()
