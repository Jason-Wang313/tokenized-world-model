# Reviewer Attacks

## Attack: The learned model is too small.

Response: Correct. The current learned/semi-learned component is a controlled VQ codebook and token transition artifact, not a benchmark-scale model. The paper should sell it as mechanism isolation and use this as motivation for benchmark validation.

## Attack: The repair has access to hand-designed diagnostics.

Response: Yes. That is the point of the controlled v1: when token aliasing is detectable through codebook, decode, physical-validity, or small pilot labels, the selected tail is repairable. The claim does not extend to hidden failures with no observable diagnostic.

## Attack: This is just a synthetic failure.

Response: The result is intentionally synthetic and finite-law-backed. The contribution is a clean diagnosis, a measurable failure mechanism, and an audit protocol. Benchmark validation is a next step, not a hidden claim.

## Attack: score-tail is being blamed for a bad scorer.

Response: The exact law separates the selection mechanism from scorer quality. score-tail amplifies whatever lies in the high-score tail. The failure is a token scorer/codebook alignment problem exposed by high-N selection.

## Attack: Tokenization is not always harmful.

Response: Agreed. The repo only studies cases where token compression aliases real physical futures in ways that matter for utility.

