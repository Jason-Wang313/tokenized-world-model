import numpy as np

from token_alias_tail_audit.law import (
    score_tail_curve,
    monte_carlo_expected_utility,
    tie_aware_expected_utility,
)


def test_tie_aware_law_matches_manual_binary_case():
    scores = [0.0, 1.0, 1.0]
    utilities = [0.0, 0.5, 1.0]
    # N=1 is the empirical utility mean.
    assert tie_aware_expected_utility(scores, utilities, 1) == 0.5
    # For N=2, max score is 0 only if both draws choose the first item.
    expected = 0.75 * (1 - (1 / 3) ** 2)
    assert np.isclose(tie_aware_expected_utility(scores, utilities, 2), expected)


def test_monte_carlo_validates_exact_law():
    scores = [0.1, 0.3, 0.3, 0.8, 1.0]
    utilities = [0.2, 0.6, 0.4, 0.7, 0.1]
    exact = tie_aware_expected_utility(scores, utilities, 8)
    mc = monte_carlo_expected_utility(scores, utilities, 8, trials=30_000, seed=2)
    assert abs(exact - mc) < 0.025


def test_curve_preserves_requested_ns():
    curve = score_tail_curve([0.0, 1.0], [0.0, 1.0], [1, 4, 16])
    assert [point.n for point in curve] == [1, 4, 16]

