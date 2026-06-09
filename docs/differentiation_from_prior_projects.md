# Differentiation From Prior Projects

This project is not a generic sequence-transformer or visual-plausibility study. It is centered on tokenized/VQ world models where continuous physical observations are compressed through a codebook before future prediction.

The core difference from video-action consistency work is the bottleneck:

- token collisions,
- quantization error,
- rare physical modes inside common tokens,
- decoder consistency,
- physical validity after decoding,
- token-specific repair and gating.

The project is also distinct from generic trajectory likelihood selection because the candidate futures are discrete world-token sequences and the selected score is explicitly tied to token likelihood, decoded reward, token critic behavior, or codebook diagnostics.

