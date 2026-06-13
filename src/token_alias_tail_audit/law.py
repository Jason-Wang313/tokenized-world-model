"""Exact finite score-tail laws for scored finite pools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class LawPoint:
    n: int
    expected_utility: float


def _arrays(scores: Iterable[float], utilities: Iterable[float]) -> tuple[np.ndarray, np.ndarray]:
    s = np.asarray(list(scores), dtype=float)
    r = np.asarray(list(utilities), dtype=float)
    if s.ndim != 1 or r.ndim != 1:
        raise ValueError("scores and utilities must be one-dimensional")
    if len(s) != len(r):
        raise ValueError("scores and utilities must have the same length")
    if len(s) == 0:
        raise ValueError("the candidate pool must be nonempty")
    return s, r


def tie_aware_expected_utility(scores: Iterable[float], utilities: Iterable[float], n: int) -> float:
    """Expected utility after selecting the max score among N iid draws.

    The draw distribution is the empirical finite pool. If several candidates tie
    for the selected maximum score, the selector breaks the tie uniformly inside
    that score group. The law is exact for any finite pool and any utility scale.
    """

    if n < 1:
        raise ValueError("n must be at least 1")
    s, r = _arrays(scores, utilities)
    m = len(s)
    expected = 0.0
    cumulative_less = 0
    for value in np.sort(np.unique(s)):
        mask = s == value
        count = int(mask.sum())
        cumulative_leq = cumulative_less + count
        probability_max_in_group = (cumulative_leq / m) ** n - (cumulative_less / m) ** n
        expected += float(r[mask].mean()) * probability_max_in_group
        cumulative_less = cumulative_leq
    return float(expected)


def score_tail_curve(
    scores: Iterable[float], utilities: Iterable[float], ns: Iterable[int]
) -> list[LawPoint]:
    return [LawPoint(int(n), tie_aware_expected_utility(scores, utilities, int(n))) for n in ns]


def select_best_index(scores: np.ndarray, rng: np.random.Generator | None = None) -> int:
    """Select an argmax index with uniform random tie breaking."""

    max_score = np.max(scores)
    ties = np.flatnonzero(scores == max_score)
    if len(ties) == 1 or rng is None:
        return int(ties[0])
    return int(rng.choice(ties))


def monte_carlo_expected_utility(
    scores: Iterable[float],
    utilities: Iterable[float],
    n: int,
    *,
    trials: int = 20_000,
    seed: int = 0,
) -> float:
    """Monte Carlo estimate of the same law, used only for validation."""

    s, r = _arrays(scores, utilities)
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(s), size=(trials, n))
    selected = np.empty(trials, dtype=float)
    for i, row in enumerate(draws):
        local_scores = s[row]
        local_best = select_best_index(local_scores, rng)
        selected[i] = r[row[local_best]]
    return float(selected.mean())

