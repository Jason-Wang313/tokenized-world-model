# V4 Cached Evidence Summary

Generated from frozen tokenized-world CSV/JSON artifacts. The v4 layer adds protocol-freeze, rubric, source-firewall, and reviewer-attack checks without rerunning the full experiment suite.

- scorecard rows: `12`
- protocol gates: `12/12`
- rubric axes: `7/7`
- reviewer attacks: `60/60`

## Scorecard

- Exact finite token-tail law: PASS - MAE 0.0028; max 0.0078
- Raw token likelihood aliasing: PASS - token gain 0.548; real drop 0.337; alias 1.000
- Decode and physical invalidity: PASS - violation 1.000; decode err 0.613
- Token-specific repair: PASS - combined gain 0.574; utility 0.629
- Pilot token-to-real calibration: PASS - pilot gain 0.763; utility 0.819
- Oracle gap kept visible: PASS - combined gap 0.327; pilot gap 0.138
- Codebook-size stress: PASS - raw range 0.038-0.089; min gain 0.553
- Tail autopsy: PASS - raw tail real 0.045; raw violation 0.814
- Semi-learned VQ artifact: PASS - K=8; collision 0.232; entropy 2.946
- Deployment gate: PASS - collect_pilot_labels: pilot calibration repairs a harmful high-N tail
- Boundary claims: PASS - hardware, external benchmark, leaderboard, and universal repair claims absent
- V4 finalization: PASS - protocol, rubric, 60 attacks, Desktop hash, GitHub push

## Protocol

- Code freeze: PASS - v4 scripts regenerate cached evidence, build the PDF, copy repo/Desktop finals, and write a manifest.
- Candidate pools frozen: PASS - The full run uses cached empirical pools; final reporting does not resample after seeing failures.
- Budgets frozen: PASS - Budgets remain 1, 2, 4, 8, 16, 32, and 64 for all selectors.
- Metrics frozen: PASS - Token likelihood, real utility, alias rate, violation rate, decode error, oracle gap, and exact-law error are fixed.
- Selectors frozen: PASS - Raw, codebook, decode, physical filter, rare, pilot, combined, and oracle selectors remain separated.
- Codebook stress frozen: PASS - The codebook-size sweep is reported as controlled stress, not external validation.
- Tail autopsy frozen: PASS - Raw, combined, and oracle selected tails are listed from cached artifacts.
- Label-spending gate frozen: PASS - Pilot token-to-real calibration is explicitly label-spending evidence.
- Boundary claims frozen: PASS - Hardware, external benchmark, leaderboard, and universal-repair claims remain absent.
- Citation surface frozen: PASS - VQ, world-model, reranking, calibration, and safety-filter citations are present in the main text.
- Harsh-reviewer loop frozen: PASS - 60 reviewer attacks generated from frozen artifacts.
- Final reporting is measurement-only: PASS - The v4 synthesis reads CSV/JSON/PDF artifacts and does not tune final thresholds.
