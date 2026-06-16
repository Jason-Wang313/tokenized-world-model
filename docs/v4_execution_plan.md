# V4 Execution Plan

Goal: make the tokenized-world paper submission-ready as a controlled mechanism audit, with no duplicate-project framing and no unsupported scope.

## Development Loop

- Use baselines, ablations, and stress cases as adversarial teachers during development.
- Keep raw token score, codebook uncertainty, decode consistency, physical filter, rare-mode reweighting, pilot token-to-real calibration, combined repair, and oracle separated.
- Use codebook-size stress, tail autopsy, exact finite-law validation, and the semi-learned VQ artifact to expose where the mechanism fails or repairs.
- Treat weak baselines as evidence, not embarrassment: codebook uncertainty and rare-mode reweighting are allowed to underperform when they reveal why the stronger repair is needed.

## Frozen Final Protocol

Before final reporting, freeze code, seeds, candidate pools, budgets, metrics, selectors, thresholds, claim gates, and source-map requirements. Final reporting must measure frozen artifacts only; it must not tune after seeing final failures.

Frozen final commands:

```bash
python experiments/v4_cached_evidence.py
python scripts/build_v4_paper.py
python scripts/run_v4_claim_audit.py
bash scripts/run_claim_audit.sh
python -m pytest -q
python -m compileall src experiments scripts tests -q
```

## Claim Gates

- Claim the exact finite law only for fixed empirical candidate pools with iid sampling and uniform tie breaking.
- Claim token-likelihood physical aliasing only for the controlled tokenized/VQ artifact.
- Claim repair only when token-specific diagnostics or pilot labels are available.
- Keep hardware deployment, external benchmark coverage, leaderboard performance, and universal repair outside the claim set.
- Report oracle gaps, weak ablations, label-spending status, and boundary language in the paper itself.

## Final Artifacts

- `paper/final/tokenized world model-v4.pdf`
- `C:\Users\wangz\OneDrive\Desktop\tokenized world model-v4.pdf`
- `paper/final/tokenized_world_model_v4_manifest.json`
- `results/v4_cached_evidence_summary.json`
- `results/v4_reviewer_attack_ledger.csv`
- `C:\Users\wangz\OneDrive\Desktop\PAPER_SOURCE_MAP.md`
