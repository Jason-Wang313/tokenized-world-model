# Final Audit

Verdict: paper-worthy v1.

This is paper-worthy v1 as a controlled diagnosis-and-repair package for tokenized/VQ world-model score-tail selection. The evidence supports a narrow claim: in the synthetic tokenized setting here, raw high-N selection improves token/internal plausibility while selecting more alias-heavy and physically invalid futures, and token-specific repair recovers much of the selected-tail utility.

Key artifact checks:

- Required commands passed locally after artifact generation.
- Failure and repair figures exist.
- A learned/semi-learned VQ artifact exists at `results/learned_vq_artifact.json`.
- Exact finite law validation has MAE `0.00276`.
- Deployment gate output is `collect_pilot_labels` with reason: pilot calibration repairs a harmful high-N tail.

Limits:

- No real-robot evidence is claimed.
- No external benchmark evidence is claimed.
- The repair result is limited to controlled settings where aliasing is detectable through codebook, decode, physical-validity, or pilot-label diagnostics.
- The project does not argue that tokenized world models are generally bad; it isolates a tail-selection failure mode.

## V4 Addendum

The v4 hardening pass keeps the same controlled claim and adds frozen protocol gates, an ICLR-style rubric map, stronger in-text citation coverage, a source firewall, and a 60-round reviewer attack ledger.

Final v4 artifact checks:

- Final Desktop file: `C:\Users\wangz\OneDrive\Desktop\tokenized world model-v4.pdf`
- Repo final file: `paper/final/tokenized world model-v4.pdf`
- Pages: `31`
- SHA-256: `43754cb2f1f1b85181658b4fe3bd606a665853c4c3f0a7119b3b06da176ed772`
- Source map row: `| tokenized world model-v4.pdf | C:\Users\wangz\tokenized world model | Jason-Wang313/tokenized-world-model |`
- Old visible Desktop files for this paper were removed.
- `python scripts/run_v4_claim_audit.py` passes on the final v4 package.
