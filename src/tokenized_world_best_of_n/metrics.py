"""Evaluation metrics for tokenized Best-of-N experiments."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

import numpy as np

from .law import monte_carlo_expected_utility, tie_aware_expected_utility
from .simulation import NS


def bootstrap_ci(values: np.ndarray, *, seed: int = 0, trials: int = 180) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = np.empty(trials)
    for i in range(trials):
        sample = rng.choice(values, size=len(values), replace=True)
        means[i] = sample.mean()
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def evaluate_methods(
    table: dict[str, np.ndarray],
    methods: dict[str, str],
    *,
    ns: Iterable[int] = NS,
    seed: int = 0,
) -> tuple[list[dict[str, float | str | int]], dict[str, np.ndarray]]:
    rows: list[dict[str, float | str | int]] = []
    selected_by_method: dict[str, np.ndarray] = {}
    pool_ids = np.unique(table["pool_id"]).astype(int)
    for method, score_key in methods.items():
        for n in ns:
            selected_indices = []
            oracle_indices = []
            for pool_id in pool_ids:
                pool_mask = table["pool_id"] == pool_id
                idx = np.flatnonzero(pool_mask)[: int(n)]
                local_scores = table[score_key][idx]
                best_local = np.flatnonzero(local_scores == local_scores.max())[0]
                selected_indices.append(idx[best_local])
                local_real = table["real_utility"][idx]
                oracle_indices.append(idx[np.argmax(local_real)])
            selected = np.asarray(selected_indices, dtype=int)
            oracle = np.asarray(oracle_indices, dtype=int)
            selected_by_method[f"{method}@{n}"] = selected
            utilities = table["real_utility"][selected]
            ci_lo, ci_hi = bootstrap_ci(utilities, seed=seed + int(n))
            oracle_utilities = table["real_utility"][oracle]
            rows.append(
                {
                    "method": method,
                    "n": int(n),
                    "selected_score_mean": float(table[score_key][selected].mean()),
                    "selected_token_likelihood_mean": float(table["token_likelihood"][selected].mean()),
                    "real_utility_mean": float(utilities.mean()),
                    "real_utility_ci_lo": ci_lo,
                    "real_utility_ci_hi": ci_hi,
                    "alias_rate": float((table["kind"][selected] == "alias").mean()),
                    "physical_violation_rate": float((table["physical_violation"][selected] > 0.45).mean()),
                    "decode_consistency_error": float(table["decode_consistency_error"][selected].mean()),
                    "token_real_gap": float(
                        table["selected_score_mean"][selected].mean()
                    )
                    if "selected_score_mean" in table
                    else float(table[score_key][selected].mean() - utilities.mean()),
                    "high_n_regret": float(oracle_utilities.mean() - utilities.mean()),
                    "oracle_gap": float(oracle_utilities.mean() - utilities.mean()),
                }
            )
    return rows, selected_by_method


def upper_tail_rank_correlation(table: dict[str, np.ndarray], score_key: str, *, top_fraction: float = 0.20) -> float:
    scores = np.asarray(table[score_key], dtype=float)
    utilities = np.asarray(table["real_utility"], dtype=float)
    cutoff = np.quantile(scores, 1.0 - top_fraction)
    mask = scores >= cutoff
    if mask.sum() < 3:
        return 0.0
    s_rank = scores[mask].argsort().argsort().astype(float)
    r_rank = utilities[mask].argsort().argsort().astype(float)
    if np.std(s_rank) < 1e-9 or np.std(r_rank) < 1e-9:
        return 0.0
    return float(np.corrcoef(s_rank, r_rank)[0, 1])


def exact_law_validation(table: dict[str, np.ndarray], *, score_key: str = "raw_score") -> dict[str, object]:
    rows = []
    errors = []
    scores = table[score_key]
    utilities = table["real_utility"]
    rng = np.random.default_rng(11)
    candidate_indices = rng.choice(len(scores), size=min(500, len(scores)), replace=False)
    s = scores[candidate_indices]
    r = utilities[candidate_indices]
    for n in NS:
        exact = tie_aware_expected_utility(s, r, n)
        mc = monte_carlo_expected_utility(s, r, n, trials=3_000, seed=100 + n)
        error = abs(exact - mc)
        errors.append(error)
        rows.append({"n": n, "exact": exact, "monte_carlo": mc, "absolute_error": error})
    return {"rows": rows, "mae": float(np.mean(errors)), "max_error": float(np.max(errors))}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
