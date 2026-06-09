# Theory

The theoretical object is a finite candidate pool of token futures with internal score `S` and real utility `R`. For each `N`, Best-of-N samples `N` iid candidates and selects the maximum-score future with uniform random tie breaking.

The expected selected utility is

```text
sum_g mean_R_g * ((U_g / m)^N - (L_g / m)^N),
```

where `g` indexes tied score groups, `m` is pool size, `L_g` counts lower-scoring candidates, and `U_g` counts candidates no higher than group `g`. This law is exact for a fixed empirical pool and applies to raw, repaired, and oracle scores.

The law predicts both success and failure. If the score aligns with real utility, larger `N` helps. If the top score group is physically aliased and low utility, larger `N` can hurt.

