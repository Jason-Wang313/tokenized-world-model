# V3 Tokenized World Model Evidence Summary

Generated from cached full artifacts. This file does not rerun experiments.

## Core Values

- law_mae: 0.002758403610848895
- raw_token_gain: 0.5484218276723245
- raw_real_drop: 0.33748536013454317
- raw_alias_high_n: 1.0
- raw_violation_high_n: 1.0
- combined_gain_high_n: 0.573822008766354
- pilot_gain_high_n: 0.7629610322684529
- combined_oracle_gap: 0.32742496004620836
- pilot_oracle_gap: 0.13828593654410948
- gate_action: collect_pilot_labels

## Scorecard

- T1 / finite tie-aware token-tail law: MAE 0.0028, max 0.0078 (supported_exact)
- T2 / raw token-likelihood physical aliasing: token gain 0.548; real drop 0.337; alias 1.000; violation 1.000 (supported_controlled)
- T3 / tail autopsy: raw tail real 0.045; combined tail real 0.631; raw violation 0.814 (supported_controlled)
- T4 / token-specific repair: combined gain 0.574; combined utility 0.629; oracle gap 0.327 (supported_controlled)
- T5 / pilot token-to-real calibration: pilot gain 0.763; pilot utility 0.819; oracle gap 0.138 (supported_controlled_with_labels)
- T6 / codebook bottleneck sweep: raw utility range 0.038-0.089; min repair gain 0.553 (supported_controlled)
- T7 / learned VQ artifact: K=8; collision 0.232; quant error 0.120; entropy 2.946 (supported_controlled)
- T8 / deployment gate: collect_pilot_labels: pilot calibration repairs a harmful high-N tail (supported_controlled)

## Self-Attack

- rounds: 50
- status counts: {'pass': 45, 'bounded': 5}
- reviewer angles: {'novelty': 2, 'scope': 3, 'overclaim': 6, 'mechanism': 7, 'theory': 3, 'leakage': 2, 'claim strength': 1, 'ablation': 2, 'baseline': 1, 'calibration': 1, 'policy': 3, 'metric': 1, 'statistics': 3, 'learned evidence': 3, 'presentation': 3, 'submission': 1, 'workflow': 3, 'reproducibility': 4, 'framing': 1}
