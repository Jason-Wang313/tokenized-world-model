# Related Work

This project connects three threads: tokenized/VQ world models, test-time candidate selection, and calibration or safety filtering for model-based planning.

The closest methodological link is finite Best-of-N inference analysis: for a fixed candidate generator and scorer, the selected real utility curve is exactly determined by the score-utility distribution. The distinct contribution here is to apply that lens to discrete world-token futures and codebook-induced physical aliasing.

The work is also adjacent to video prediction and action-consistency studies, but the mechanism here is not visual plausibility alone. The central object is the tokenization bottleneck and the way its discrete cells can hide physically important distinctions.

