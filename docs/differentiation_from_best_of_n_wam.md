# Differentiation From Best-of-N WAM

WAM-style work studies imagined-vs-real dynamics mismatch: a rollout generator imagines continuous action-conditioned futures, a scorer selects among them, and real rollout utility can diverge from imagined utility.

This repo studies a different scientific object:

- the discrete tokenizer/codebook bottleneck,
- token likelihood and token transition plausibility,
- hidden physical states compressed into the same token,
- decoded token futures,
- token-to-real aliasing in the selected upper tail.

The shared ingredient is the finite Best-of-N law and audit discipline. The mechanism, metrics, diagnostics, repairs, figures, and paper framing are token-specific.

