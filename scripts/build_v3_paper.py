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
FINAL_NAME = "tokenized world model-v3.pdf"
OLD_NAME = "tokenized world model-v2.pdf"
GITHUB_REPO = "Jason-Wang313/tokenized-world-model"
SOURCE_MAP_ROW = (
    f"| `{FINAL_NAME}` | `{ROOT}` | `{GITHUB_REPO}` |"
)
MIN_PAGES = 25


def run(cmd: list[str], cwd: Path = ROOT) -> None:
    print("+ " + " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


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


def update_source_map() -> None:
    text = SOURCE_MAP.read_text(encoding="utf-8")
    lines = text.splitlines()
    replaced = False
    for idx, line in enumerate(lines):
        if "tokenized world model" in line or GITHUB_REPO in line:
            lines[idx] = SOURCE_MAP_ROW
            replaced = True
    if not replaced:
        lines.append(SOURCE_MAP_ROW)
    SOURCE_MAP.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    run([sys.executable, str(ROOT / "scripts" / "prepare_v3_evidence.py")])
    run(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(PAPER_DIR / "build.ps1"),
        ]
    )

    compiled_pdf = PAPER_DIR / "main.pdf"
    if not compiled_pdf.exists() or compiled_pdf.stat().st_size <= 0:
        raise RuntimeError("LaTeX build did not produce a non-empty main.pdf")

    pages = page_count(compiled_pdf)
    if pages < MIN_PAGES:
        raise RuntimeError(f"final PDF has {pages} pages, below {MIN_PAGES}")

    final_dir = ROOT / "paper" / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    repo_final_pdf = final_dir / FINAL_NAME
    desktop_final_pdf = DESKTOP / FINAL_NAME
    shutil.copy2(compiled_pdf, repo_final_pdf)
    shutil.copy2(compiled_pdf, desktop_final_pdf)

    old_desktop_pdf = DESKTOP / OLD_NAME
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
        "repo_pdf": str(repo_final_pdf),
        "desktop_pdf": str(desktop_final_pdf),
        "source_map": str(SOURCE_MAP),
        "source_map_row": SOURCE_MAP_ROW,
        "github_repo": GITHUB_REPO,
        "built_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    manifest_path = final_dir / "tokenized_world_model_v3_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"finalized {FINAL_NAME}")
    print(f"pages: {pages}")
    print(f"sha256: {pdf_hash}")
    print(f"repo pdf: {repo_final_pdf}")
    print(f"desktop pdf: {desktop_final_pdf}")


if __name__ == "__main__":
    main()
