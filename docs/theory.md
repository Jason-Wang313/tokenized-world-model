# Theory

## Setup

Let `x_t` be a continuous physical state or observation. A tokenizer maps it to a discrete world token through `q(c_t | x_t)`, with codebook `C = {z_1, ..., z_K}` and decoder `d(c_t)`. A tokenized world model predicts token futures

```text
c_{t+1:t+H} ~ p(c_{t+1:t+H} | c_t, a, goal).
```

Each generated token future is decoded into a future observation or state estimate. A planner scores the candidate with an internal score `S`: token likelihood, token plausibility, decoded reward, token critic value, or a mixture. Real utility `R` is measured separately after decoding or executing the implied future in the real evaluation environment.

Best-of-N selection draws candidates `Y_1, ..., Y_N` from the token generator and returns

```text
Y* = argmax_i S(Y_i),
```

with random tie breaking among candidates sharing the maximum score.

The target failure mode is token-likelihood physical aliasing: different physical futures collapse into the same or nearby discrete token pattern, and the high-score token tail contains physically invalid decoded futures.

## Exact Finite Law

For a fixed finite candidate pool with scores `S_i` and utilities `R_i`, group candidates by equal score. For score group `g`, let `mean_R_g` be the mean real utility inside the tied group, `m` the pool size, `L_g` the number of candidates with strictly lower score, and `U_g` the number with score less than or equal to the group score. The exact expected selected utility under `N` iid empirical draws is

```text
E[R(Y*)] = sum_g mean_R_g * ((U_g / m)^N - (L_g / m)^N).
```

This is tie-aware because a selected maximum score group contributes the average real utility inside that group.

## Edge Cases

- `N = 1`: the law reduces to the empirical mean utility.
- Perfect alignment: if score order matches real utility order, expected utility increases with `N`.
- Anti-alignment: if the highest score group has low real utility, expected utility can decrease as `N` grows.
- All scores tied: selection is uniform for every `N`, so expected utility is constant.
- Empty pools are invalid; the implementation raises an error.

## Oracle And Anti-Aligned Examples

An oracle scorer ranks candidates by `R`, so Best-of-N stresses genuinely useful futures. An anti-aligned token scorer ranks alias-heavy futures above physically valid futures; larger `N` then increases the probability that the selected candidate comes from the bad high-score token tail.

The experiments instantiate this with token futures whose likelihood is high because they follow common codebook transitions, while their hidden physical mode, decoded contact state, or collision condition is wrong.

## Finite-Pool Expected Utility

The law is not a training guarantee. It is a conditional inference law: once the generator, tokenizer, scorer, and candidate distribution are fixed, the expected selected real utility curve is determined by the joint empirical distribution of `(S, R)`.

The same law applies to raw token likelihood, decoded reward, repaired scores, and oracle real utility. The repo uses this to separate a scorer failure from the mechanics of Best-of-N selection.

## Monte Carlo Validation

The script `bash scripts/run_all.sh` computes the exact law on a held finite pool and compares it with Monte Carlo repeated Best-of-N draws. The audit records mean absolute error in `results/exact_law_validation.json`.

