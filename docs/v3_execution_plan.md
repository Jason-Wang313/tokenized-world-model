# V3 Execution Plan: Tokenized World Model

## Current Claim

The paper claims that tokenized/VQ world-model planning can suffer a selection-time aliasing failure: raw high-budget selection raises token likelihood or decoded token score while selected real utility falls because the chosen future exploits codebook collisions, hidden-mode aliasing, quantization gaps, or physically invalid decodes.

The positive claims must stay narrow:

- exact finite tie-aware score-tail law for fixed empirical token-future pools;
- controlled evidence for token-likelihood physical aliasing;
- token-specific diagnostics and repairs for detectable aliasing;
- semi-learned VQ/tokenized artifact with codebook, transition, decode-validity, and repair evidence.

Unsupported boundary claims must remain explicit: no robot-hardware evidence, no external benchmark coverage, no state-of-the-art tokenized model result, no universal harm from larger candidate pools, and no universal repair guarantee.

## Gaps in the 11-Page Baseline

- The current PDF is 11 pages and cannot be considered submission-ready under the v3 standard.
- The current narrative is good but too compact: it underexposes the codebook bottleneck, tail autopsy, diagnostics, learned VQ artifact, gate logic, and repair limitations.
- It has only six figures and one compact table; the evidence needs synthesis figures/tables, expanded stress discussion, and a self-attack appendix.
- It must avoid looking like a generic candidate-budget wrapper by making token-codebook aliasing, physical decode validity, and token-to-real calibration dominate every section.

## Target Evidence and Experiments

Use cached audited artifacts first, because the repo already has CPU-local full outputs:

- `results/metrics_main.csv` for raw and repaired selected-tail curves;
- `results/tail_autopsy.csv` for selected bad-tail mechanisms;
- `results/codebook_bottleneck.csv` for codebook size, rare modes, and quantization;
- `results/exact_law_validation.json` for finite-law Monte Carlo validation;
- `results/learned_vq_artifact.json` for the semi-learned tokenized artifact;
- `results/claims_status.json` and `results/summary.json` for claim gates;
- existing figures 1-6 for failure, repair, codebook bottleneck, decode validity, exact law, and alias atlas.

If the cached artifacts are too thin, add RAM-light synthesis or small sequential extensions rather than rerunning a heavy all-at-once job.

## Baselines, Ablations, Stress Tests

Baselines:
- raw token-likelihood/decode-reward score;
- random selection;
- oracle real-utility selector;
- individual token diagnostics;
- pilot token-to-real calibrator;
- deployment gate.

Ablations and diagnostic comparisons:
- codebook uncertainty only;
- alias detection only;
- decode consistency only;
- physical-validity filter only;
- rare-mode reweighting only;
- combined repair;
- pilot calibration separated from no-label diagnostics.

Stress tests and failure cases:
- codebook-size sweep;
- rare-mode/hidden-mode aliasing;
- quantization-error bottleneck;
- physical invalidity such as teleportation, collision, impossible contact, and hidden-mode mismatch;
- exact-law vs Monte Carlo;
- tail autopsy of selected raw vs repaired futures;
- gate behavior when pilot labels are needed.

## V3 Artifacts to Add

Generate cached v3 synthesis artifacts:

- v3 evidence summary JSON/MD;
- v3 scorecard CSV and LaTeX table;
- v3 50-round reviewer self-attack ledger CSV and LaTeX table;
- new figures summarizing claim scorecard, repair tiers, codebook stress, tail autopsy, learned VQ evidence, and attack coverage;
- final PDF manifest with pages, SHA, Desktop path, and source-map expectation.

## Writing Expansion

Rewrite and expand the ICLR manuscript into at least 25 pages:

- abstract with narrow token-aliasing claim and explicit nonclaims;
- introduction centered on token likelihood, codebook collisions, decode validity, hidden modes, and physical aliasing;
- finite-law section framed as audit machinery;
- tokenized/VQ setup and diagnostics section;
- RQ-organized experiments;
- expanded related work on VQ/tokenized world models, world-model planning, reranking, calibration, and safety filters;
- strict limitations and claim discipline;
- reproducibility details;
- appendices for proof, generator details, VQ artifact, diagnostics, stress gallery, gate policy, artifact inventory, and 50-round self-attack ledger.

## Page-Count Strategy

The minimum accepted final PDF length is 25 pages. Length must come from real content:

- richer method and diagnostics sections;
- additional v3 synthesis figures and tables;
- detailed stress and tail-autopsy appendices;
- expanded related work and limitations;
- self-attack ledger and artifact checklist.

## RAM-Light Execution Strategy

- Prefer a cached evidence script reading CSV/JSON artifacts and writing compact summaries/figures.
- Avoid replacing full artifacts with smoke-mode outputs.
- Run experiments sequentially only if a missing evidence gap is found.
- Keep all generated summaries compact: CSV, JSON, and PNG figures; avoid holding large candidate arrays in memory.
- Validate with build/audit/test commands after all content changes.

## Final Acceptance Checklist

- PDF has at least 25 pages and is built from `paper/iclr/main.tex`.
- Final repo PDF is `paper/final/tokenized world model-v3.pdf`.
- Desktop has `tokenized world model-v3.pdf`; old `tokenized world model-v2.pdf` is absent.
- `PAPER_SOURCE_MAP.md` maps `tokenized world model-v3.pdf` to `C:\Users\wangz\tokenized world model` and `Jason-Wang313/tokenized-world-model`.
- v3 attack ledger has exactly 50 reviewer attacks.
- Claims remain limited to controlled tokenized/VQ evidence.
- No real-robot, external benchmark, state-of-the-art, universal-harm, or universal-repair overclaim appears.
- `python scripts/prepare_v3_evidence.py`, paper build, `python scripts/run_v3_claim_audit.py`, `bash scripts/run_claim_audit.sh`, `python -m compileall`, and `pytest` pass.
- Final commit is pushed to GitHub and the remote `main` SHA is verified.
