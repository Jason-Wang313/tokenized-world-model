"""Token-specific repair scores and deployment gates."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


ALLOWED_GATE_OUTPUTS = {
    "allow_high_n",
    "stop_early",
    "collect_pilot_labels",
    "retokenize_or_refine_codebook",
    "block_high_n",
}


@dataclass(frozen=True)
class GateDecision:
    action: str
    reason: str

    def __post_init__(self) -> None:
        if self.action not in ALLOWED_GATE_OUTPUTS:
            raise ValueError(f"invalid gate action: {self.action}")


def feature_matrix(table: dict[str, np.ndarray]) -> np.ndarray:
    columns = [
        table["raw_score"],
        table["token_likelihood"],
        table["decoded_reward"],
        table["alias_probability"],
        table["quantization_error"],
        table["decode_consistency_error"],
        table["physical_violation"],
        table["rare_token_bonus"],
    ]
    return np.column_stack(columns)


def fit_linear_calibrator(table: dict[str, np.ndarray], *, pilot_fraction: float = 0.16) -> np.ndarray:
    """Fit a tiny ridge regressor from token diagnostics to real utility."""

    x = feature_matrix(table)
    y = table["real_utility"]
    n = max(12, int(len(y) * pilot_fraction))
    x_pilot = x[:n]
    y_pilot = y[:n]
    x_mean = x_pilot.mean(axis=0)
    x_std = x_pilot.std(axis=0) + 1e-6
    x_scaled = (x_pilot - x_mean) / x_std
    design = np.column_stack([np.ones(len(x_scaled)), x_scaled])
    penalty = np.eye(design.shape[1]) * 1e-3
    penalty[0, 0] = 0.0
    weights = np.linalg.solve(design.T @ design + penalty, design.T @ y_pilot)
    return np.concatenate([weights, x_mean, x_std])


def apply_linear_calibrator(table: dict[str, np.ndarray], packed: np.ndarray) -> np.ndarray:
    n_features = feature_matrix(table).shape[1]
    weights = packed[: n_features + 1]
    x_mean = packed[n_features + 1 : 2 * n_features + 1]
    x_std = packed[2 * n_features + 1 :]
    x_scaled = (feature_matrix(table) - x_mean) / x_std
    design = np.column_stack([np.ones(len(x_scaled)), x_scaled])
    return np.clip(design @ weights, -0.1, 1.05)


def add_repair_scores(table: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    out = {k: np.array(v, copy=True) for k, v in table.items()}
    alias = out["alias_probability"]
    qerr = out["quantization_error"]
    decode = out["decode_consistency_error"]
    physical = out["physical_violation"]
    raw = out["raw_score"]
    rare = out["rare_token_bonus"]

    out["codebook_uncertainty_score"] = raw - 0.85 * alias - 0.25 * qerr
    out["decode_consistency_score"] = raw - 0.95 * decode - 0.75 * physical
    out["physical_filter_score"] = np.where(physical > 0.45, raw - 2.0, raw - 0.35 * alias)
    out["rare_mode_reweight_score"] = raw - 0.75 * alias + 0.35 * rare - 0.55 * physical
    packed = fit_linear_calibrator(out)
    out["calibrated_real_score"] = apply_linear_calibrator(out, packed)
    out["combined_repair_score"] = (
        0.15 * out["codebook_uncertainty_score"]
        + 0.15 * out["decode_consistency_score"]
        + 0.25 * out["physical_filter_score"]
        + 0.45 * out["calibrated_real_score"]
    )
    out["calibrator_weights"] = packed
    return out


def deployment_gate(summary: dict[str, float]) -> GateDecision:
    alias = summary.get("alias_rate_at_high_n", 0.0)
    violation = summary.get("violation_rate_at_high_n", 0.0)
    raw_delta = summary.get("raw_real_delta_high_vs_n1", 0.0)
    repair_gain = summary.get("repair_gain_at_high_n", 0.0)
    law_error = summary.get("exact_law_mae", 1.0)

    if alias > 0.55 and violation > 0.45 and repair_gain < 0.03:
        return GateDecision("retokenize_or_refine_codebook", "aliasing remains high after repair")
    if alias > 0.42 and raw_delta < -0.02 and repair_gain > 0.04:
        return GateDecision("collect_pilot_labels", "pilot calibration repairs a harmful high-N tail")
    if alias > 0.50 or violation > 0.55:
        return GateDecision("block_high_n", "selected high-N tail is physically invalid")
    if raw_delta < -0.01:
        return GateDecision("stop_early", "raw utility declines with larger N")
    if law_error < 0.03 and alias < 0.25:
        return GateDecision("allow_high_n", "tail diagnostics are aligned enough for controlled use")
    return GateDecision("collect_pilot_labels", "diagnostics are inconclusive")

