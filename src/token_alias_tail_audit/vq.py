"""Small CPU-only VQ/tokenizer utilities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class MiniVQ:
    codebook: np.ndarray

    @classmethod
    def fit(cls, observations: np.ndarray, codebook_size: int, *, seed: int = 0, steps: int = 16) -> "MiniVQ":
        if codebook_size < 2:
            raise ValueError("codebook_size must be at least 2")
        x = np.asarray(observations, dtype=float)
        if x.ndim != 2:
            raise ValueError("observations must be a 2D array")
        rng = np.random.default_rng(seed)
        init = rng.choice(len(x), size=codebook_size, replace=False)
        centers = x[init].copy()
        for _ in range(steps):
            distances = ((x[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
            assignment = distances.argmin(axis=1)
            for k in range(codebook_size):
                mask = assignment == k
                if mask.any():
                    centers[k] = x[mask].mean(axis=0)
                else:
                    centers[k] = x[rng.integers(0, len(x))]
        return cls(centers)

    def predict(self, observations: np.ndarray) -> np.ndarray:
        x = np.asarray(observations, dtype=float)
        distances = ((x[:, None, :] - self.codebook[None, :, :]) ** 2).sum(axis=2)
        return distances.argmin(axis=1).astype(int)

    def quantization_error(self, observations: np.ndarray) -> np.ndarray:
        x = np.asarray(observations, dtype=float)
        tokens = self.predict(x)
        return np.sqrt(((x - self.codebook[tokens]) ** 2).sum(axis=1))


def build_synthetic_observations(
    *,
    n: int = 2_500,
    rare_mode_fraction: float = 0.14,
    seed: int = 0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create observations with a hidden physical mode omitted from tokenization."""

    rng = np.random.default_rng(seed)
    position = rng.beta(2.1, 2.1, size=n)
    velocity = rng.normal(0.0, 0.22, size=n)
    rare_band = (position > 0.42) & (position < 0.62)
    hidden = (rng.random(n) < rare_mode_fraction + 0.38 * rare_band).astype(int)
    observations = np.column_stack([position, velocity])
    full_state = np.column_stack([position, velocity, hidden])
    return observations, full_state, hidden


def token_entropy(tokens: np.ndarray) -> float:
    counts = np.bincount(np.asarray(tokens, dtype=int))
    counts = counts[counts > 0]
    p = counts / counts.sum()
    return float(-(p * np.log2(p)).sum())


def collision_rate(tokens: np.ndarray, hidden_modes: np.ndarray) -> float:
    """Weighted hidden-mode alias mass inside token cells."""

    tokens = np.asarray(tokens, dtype=int)
    hidden_modes = np.asarray(hidden_modes, dtype=int)
    total = len(tokens)
    collisions = 0
    for token in np.unique(tokens):
        modes = hidden_modes[tokens == token]
        counts = np.bincount(modes, minlength=2)
        collisions += int(counts.sum() - counts.max())
    return float(collisions / total)


def token_alias_statistics(tokens: np.ndarray, hidden_modes: np.ndarray) -> dict[int, float]:
    """Return per-token probability that hidden mode is ambiguous."""

    out: dict[int, float] = {}
    tokens = np.asarray(tokens, dtype=int)
    hidden_modes = np.asarray(hidden_modes, dtype=int)
    for token in np.unique(tokens):
        modes = hidden_modes[tokens == token]
        counts = np.bincount(modes, minlength=2).astype(float)
        out[int(token)] = float(1.0 - counts.max() / max(counts.sum(), 1.0))
    return out


def transition_matrix(tokens: np.ndarray, codebook_size: int, *, smoothing: float = 0.1) -> np.ndarray:
    """Semi-learned token transition counts from neighboring observations."""

    matrix = np.full((codebook_size, codebook_size), smoothing, dtype=float)
    for a, b in zip(tokens[:-1], tokens[1:]):
        matrix[int(a), int(b)] += 1.0
    matrix /= matrix.sum(axis=1, keepdims=True)
    return matrix
