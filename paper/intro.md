# Introduction

Tokenized world models are attractive because discrete latent futures can be compact, compositional, and easier to model than raw continuous observations. But the discrete bottleneck creates a planning-specific risk. A token future can be likely under the token model while representing several physically different decoded futures, only some of which are useful.

Best-of-N selection stresses this issue. If the selected score is token likelihood, decoded reward, or a token critic that is misaligned with real utility, increasing `N` concentrates selection on the upper tail of the internal score distribution. When that tail is alias-heavy, selected plausibility can rise while real utility falls.

This paper isolates that mechanism in controlled experiments. The goal is not to reject tokenized world models, but to make one failure mode measurable and repairable.

