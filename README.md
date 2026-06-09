# When World Tokens Lie

Best-of-N inference laws for tokenized world models.

This repository studies a narrow controlled question: when a world model compresses continuous states or observations into discrete world tokens, what happens when planning selects the highest-scoring future from a larger test-time candidate pool?

The central failure mode is **token-likelihood physical aliasing**. A token future can look increasingly plausible under token likelihood or decoded reward as `N` grows while the real decoded/executed utility stagnates or worsens because the selected upper tail exploits codebook collisions, hidden-mode aliasing, or physical-validity gaps.

The repo is diagnosis plus controlled repair. It tests token-specific safeguards: codebook uncertainty, alias detection, decode-consistency checks, physical-validity filters, rare-mode reweighting, and small pilot token-to-real calibration. The evidence is synthetic and CPU-local; it is not a real-robot result and not a claim that tokenized world models are generally bad.

## Quickstart

```bash
bash scripts/run_smoke.sh
bash scripts/run_all.sh
bash scripts/run_claim_audit.sh
pytest
```

## What Is Included

- Exact finite tie-aware Best-of-N law for scored token-future pools.
- Controlled token aliasing toy where physically distinct states collapse into the same token.
- Semi-learned VQ/tokenized world model with a learned codebook and transition statistics.
- Codebook bottleneck stress test over codebook size, rare modes, and quantization error.
- Decode/physical-validity diagnostics for teleportation, collision, impossible contact, and hidden-mode mismatch.
- Repair selectors and a deployment gate that can block or reduce high-`N` selection when aliasing is detected.
- Figures, claim audit, paper skeleton, reviewer-risk notes, and final audit.

## Main Artifacts

- `docs/theory.md`: formal setup and exact finite law.
- `results/metrics_main.csv`: raw and repaired Best-of-N curves.
- `results/codebook_bottleneck.csv`: codebook-size stress sweep.
- `results/exact_law_validation.json`: Monte Carlo validation of the exact law.
- `results/learned_vq_artifact.json`: learned/semi-learned tokenized model artifact.
- `results/claims_status.json`: claim-to-evidence status.
- `figures/figure1_token_likelihood_physical_aliasing.png`
- `figures/figure2_repair_comparison.png`
- `figures/figure3_codebook_bottleneck_curve.png`
- `figures/figure4_decode_validity_diagnostics.png`
- `figures/figure5_exact_law_validation.png`
- `figures/figure6_alias_atlas.png`

## Scope

This is a controlled paper package for tokenized/VQ world-model planning. It is distinct from imagined-vs-real dynamics mismatch in WAM-style studies: here the scientific object is the discrete codebook/token bottleneck, token likelihood, decode consistency, and token-to-real aliasing. The repair claims are limited to settings where aliasing is measurable by token-specific diagnostics or a small pilot calibration set.

