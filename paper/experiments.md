# Experiments

The experiments use `N = {1,2,4,8,16,32,64}`.

Experiment A is a controlled aliasing toy where physically different hidden modes map to the same token cell.

Experiment B trains a small VQ tokenizer and token transition model on generated observations, yielding the learned artifact in `results/learned_vq_artifact.json`.

Experiment C sweeps codebook size to stress collision rate, quantization error, rare modes, and high-N regret.

Experiment D logs decode and physical-validity diagnostics: collision, teleportation, hidden-mode error, and decode-consistency error.

Experiment E compares repair selectors and the deployment gate against raw token scoring and an oracle real-utility selector.

