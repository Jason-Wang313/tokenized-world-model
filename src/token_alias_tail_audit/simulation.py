"""Synthetic tokenized world-model candidate pools."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .vq import (
    MiniVQ,
    build_synthetic_observations,
    collision_rate,
    token_alias_statistics,
    token_entropy,
    transition_matrix,
)


NS = (1, 2, 4, 8, 16, 32, 64)


@dataclass(frozen=True)
class LearnedVQArtifact:
    codebook_size: int
    quantization_error_mean: float
    collision_rate: float
    token_entropy: float
    transition_self_probability: float


def train_tokenized_world_model(
    *, codebook_size: int = 8, seed: int = 0, n: int = 1_200
) -> tuple[MiniVQ, dict[str, object]]:
    observations, _full_state, hidden = build_synthetic_observations(n=n, seed=seed)
    vq = MiniVQ.fit(observations, codebook_size, seed=seed)
    tokens = vq.predict(observations)
    qerr = vq.quantization_error(observations)
    trans = transition_matrix(tokens, codebook_size)
    artifact = LearnedVQArtifact(
        codebook_size=codebook_size,
        quantization_error_mean=float(qerr.mean()),
        collision_rate=collision_rate(tokens, hidden),
        token_entropy=token_entropy(tokens),
        transition_self_probability=float(np.diag(trans).mean()),
    )
    metadata = {
        "artifact": artifact,
        "tokens": tokens,
        "hidden": hidden,
        "quantization_error_by_token": {
            int(k): float(qerr[tokens == k].mean()) for k in np.unique(tokens)
        },
        "alias_probability_by_token": token_alias_statistics(tokens, hidden),
        "token_frequency": {
            int(k): int((tokens == k).sum()) for k in np.unique(tokens)
        },
        "transition_matrix": trans,
    }
    return vq, metadata


def _choose_token(
    rng: np.random.Generator,
    token_frequency: dict[int, int],
    alias_probability: dict[int, float],
    *,
    prefer_alias: bool,
    prefer_rare: bool = False,
) -> int:
    tokens = np.array(sorted(token_frequency), dtype=int)
    counts = np.array([token_frequency[int(t)] for t in tokens], dtype=float)
    alias = np.array([alias_probability.get(int(t), 0.0) for t in tokens], dtype=float)
    if prefer_alias:
        weights = counts * (0.05 + alias) ** 2
    elif prefer_rare:
        weights = 1.0 / np.maximum(counts, 1.0)
    else:
        weights = counts * (1.0 - 0.6 * alias)
    weights = weights / weights.sum()
    return int(rng.choice(tokens, p=weights))


def generate_candidate_table(
    *,
    codebook_size: int = 8,
    n_pools: int = 220,
    pool_size: int = 64,
    seed: int = 0,
    rare_mode_fraction: float = 0.14,
) -> tuple[dict[str, np.ndarray], dict[str, object]]:
    """Generate candidate token futures and separate real utilities."""

    _vq, meta = train_tokenized_world_model(codebook_size=codebook_size, seed=seed)
    rng = np.random.default_rng(seed + 31)
    token_frequency: dict[int, int] = meta["token_frequency"]  # type: ignore[assignment]
    alias_probability: dict[int, float] = meta["alias_probability_by_token"]  # type: ignore[assignment]
    qerr_by_token: dict[int, float] = meta["quantization_error_by_token"]  # type: ignore[assignment]
    max_qerr = max(qerr_by_token.values()) + 1e-6
    max_count = max(token_frequency.values())

    bottleneck = float(np.clip((14 - codebook_size) / 12, 0.0, 1.0))
    p_alias = np.clip(0.12 + 0.42 * bottleneck + 0.50 * rare_mode_fraction, 0.08, 0.70)
    p_rare_good = np.clip(0.16 - 0.05 * bottleneck, 0.05, 0.18)
    p_bad = 0.08

    n_total = n_pools * pool_size
    columns: dict[str, list[float | int | str]] = {
        "pool_id": [],
        "candidate_id": [],
        "token_id": [],
        "kind": [],
        "raw_score": [],
        "token_likelihood": [],
        "decoded_reward": [],
        "real_utility": [],
        "alias_probability": [],
        "quantization_error": [],
        "decode_consistency_error": [],
        "physical_violation": [],
        "collision_violation": [],
        "teleport_violation": [],
        "hidden_mode_error": [],
        "rare_token_bonus": [],
    }

    for pool_id in range(n_pools):
        for candidate_id in range(pool_size):
            u = rng.random()
            if u < p_alias:
                kind = "alias"
                token_id = _choose_token(
                    rng, token_frequency, alias_probability, prefer_alias=True
                )
            elif u < p_alias + p_rare_good:
                kind = "rare_good"
                token_id = _choose_token(
                    rng, token_frequency, alias_probability, prefer_alias=False, prefer_rare=True
                )
            elif u < p_alias + p_rare_good + p_bad:
                kind = "bad_low"
                token_id = _choose_token(
                    rng, token_frequency, alias_probability, prefer_alias=False
                )
            else:
                kind = "valid"
                token_id = _choose_token(
                    rng, token_frequency, alias_probability, prefer_alias=False
                )

            alias_p = alias_probability.get(token_id, 0.0)
            qerr = qerr_by_token.get(token_id, 0.0) / max_qerr
            freq = token_frequency[token_id] / max_count
            rare_bonus = float(np.clip(1.0 - freq, 0.0, 1.0))

            if kind == "alias":
                token_likelihood = rng.normal(1.22 + 0.12 * bottleneck, 0.07)
                decoded_reward = rng.normal(0.78, 0.08)
                physical = rng.uniform(0.62, 1.0)
                real_utility = rng.normal(0.18 - 0.10 * bottleneck, 0.09)
                hidden_error = rng.uniform(0.55, 1.0)
            elif kind == "rare_good":
                token_likelihood = rng.normal(0.48, 0.08)
                decoded_reward = rng.normal(0.66, 0.09)
                physical = rng.uniform(0.0, 0.12)
                real_utility = rng.normal(0.88, 0.06)
                hidden_error = rng.uniform(0.0, 0.12)
            elif kind == "bad_low":
                token_likelihood = rng.normal(0.30, 0.10)
                decoded_reward = rng.normal(0.22, 0.10)
                physical = rng.uniform(0.20, 0.60)
                real_utility = rng.normal(0.25, 0.10)
                hidden_error = rng.uniform(0.12, 0.45)
            else:
                token_likelihood = rng.normal(0.68, 0.10)
                decoded_reward = rng.normal(0.62, 0.10)
                physical = rng.uniform(0.0, 0.18)
                real_utility = rng.normal(0.64 - 0.05 * alias_p, 0.08)
                hidden_error = rng.uniform(0.0, 0.18)

            collision = float(np.clip(0.35 * physical + 0.65 * alias_p + rng.normal(0, 0.04), 0, 1))
            teleport = float(np.clip(0.62 * physical + rng.normal(0, 0.05), 0, 1))
            decode_consistency = float(
                np.clip(0.48 * alias_p + 0.37 * physical + 0.22 * qerr + rng.normal(0, 0.04), 0, 1)
            )
            raw_score = float(
                0.70 * token_likelihood
                + 0.35 * decoded_reward
                - 0.04 * qerr
                + rng.normal(0, 0.035)
            )
            real_utility = float(np.clip(real_utility - 0.10 * physical, -0.05, 1.0))

            values = {
                "pool_id": pool_id,
                "candidate_id": candidate_id,
                "token_id": token_id,
                "kind": kind,
                "raw_score": raw_score,
                "token_likelihood": float(token_likelihood),
                "decoded_reward": float(decoded_reward),
                "real_utility": real_utility,
                "alias_probability": float(alias_p),
                "quantization_error": float(qerr),
                "decode_consistency_error": decode_consistency,
                "physical_violation": float(physical),
                "collision_violation": collision,
                "teleport_violation": teleport,
                "hidden_mode_error": float(hidden_error),
                "rare_token_bonus": rare_bonus,
            }
            for key, value in values.items():
                columns[key].append(value)

    table: dict[str, np.ndarray] = {}
    for key, value in columns.items():
        if key == "kind":
            table[key] = np.asarray(value, dtype=object)
        else:
            table[key] = np.asarray(value)
    table["n_total"] = np.asarray([n_total])
    return table, meta
