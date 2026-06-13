# Method

The pipeline has four parts.

1. Train a small VQ tokenizer on continuous observations while omitting a hidden physical mode from the tokenized feature space.
2. Generate candidate discrete token futures from the learned codebook and transition statistics.
3. Score candidates with raw token likelihood and decoded reward, then evaluate real utility separately with hidden-mode and physical-validity penalties.
4. Compare raw score-tail selection with token-specific repair scores and an oracle real-utility selector.

Repairs include codebook uncertainty penalties, alias detection, decode-consistency penalties, hard physical-validity filtering, rare-mode reweighting, and a small ridge calibrator trained on pilot real-utility labels.

