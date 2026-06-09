"""Best-of-N inference diagnostics for tokenized world models."""

from .law import best_of_n_curve, tie_aware_expected_utility

__all__ = ["best_of_n_curve", "tie_aware_expected_utility"]

