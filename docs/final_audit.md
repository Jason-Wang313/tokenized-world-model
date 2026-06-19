# Final Audit

Verdict: v4 submission package is ready for the scoped controlled-mechanism claim.

The final paper is not a broad hardware or external-benchmark submission. It is a controlled tokenized/VQ world-model tail-selection audit: raw high-N token selection improves token likelihood while selecting alias-heavy, physically invalid futures, and token-specific repair plus pilot token-to-real calibration recovers much of the selected-tail utility while leaving oracle gaps visible.

Final v4 artifact checks, verified on 2026-06-19:

- Final Desktop file: `C:\Users\wangz\OneDrive\Desktop\tokenized world model-v4.pdf`
- Repo final file: `paper/final/tokenized world model-v4.pdf`
- Pages: `31`
- SHA-256: `ba9837e6555fabd1c6947aab43f813d50194d48adb60f6c6439996976a2c1f56`
- Source map row: `| tokenized world model-v4.pdf | C:\Users\wangz\tokenized world model | Jason-Wang313/tokenized-world-model |`
- Old visible Desktop files for this paper were removed.
- The repo and Desktop PDFs have identical SHA-256 hashes.
- Visual QA rendered all 31 pages after the guarded final build and inspected pages 1, 11, 30, and 31; the same v4 layout was also inspected on pages 4, 5, 10, 18, 19, 20, 26, 27, 28, and 29 before the final metadata-only rebuild.

Verification commands passed:

- `python -m compileall src experiments scripts tests -q`
- `python -m pytest -q`
- `python scripts/run_v4_claim_audit.py`
- strict LaTeX log scan for undefined citations/references, rerun warnings, overfulls, duplicate destinations, and fatal errors
- `pdfinfo` page-count check
- repo/Desktop `Get-FileHash -Algorithm SHA256` equality check

V4 hardening added frozen protocol gates, an ICLR-style rubric map, stronger in-text citation coverage, source-firewall language, chunked readable evidence tables, a 60-round reviewer attack ledger, and a manifest tying the source folder, GitHub remote, Desktop PDF, source map, page count, and artifact hash together.

Scope limits:

- No real-robot evidence is claimed.
- No external benchmark or leaderboard evidence is claimed.
- The repair result is limited to controlled settings where aliasing is detectable through codebook, decode, physical-validity, rare-mode, or pilot-label diagnostics.
- The paper does not argue that tokenized world models are generally bad; it isolates a tail-selection failure mode and gates deployment on additional labels or abstention.
