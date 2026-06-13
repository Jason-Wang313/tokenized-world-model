# Claims

## Supported In This Repo

- In the controlled tokenized/VQ setting, raw score-tail selection can improve selected token likelihood while reducing selected real utility.
- Codebook collision, alias probability, quantization error, decode-consistency error, and physical-validity diagnostics identify the bad selected tail.
- Token-specific repair scores and a small pilot token-to-real calibrator improve high-N selected utility in the controlled experiments.
- The finite tie-aware score-tail law exactly predicts expected selected utility for fixed empirical token-future pools.

## Not Claimed

- General failure of tokenized world models.
- Universal harm from larger candidate pools.
- Universal success of codebook uncertainty or calibration.
- Deployment evidence on physical robots.
- External benchmark coverage.
- State-of-the-art tokenized world-model performance.

## Claim Discipline

Every positive result should point to an artifact in `results/` or `figures/`. If an experiment is controlled, the claim must say so. If a repair works because aliasing is detectable, the claim must keep that condition visible.

