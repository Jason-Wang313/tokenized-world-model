"""Figure generation for the tokenized world-model experiments."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def _rows_for(rows: list[dict[str, object]], method: str) -> list[dict[str, object]]:
    return sorted([r for r in rows if r["method"] == method], key=lambda r: int(r["n"]))


def plot_failure(rows: list[dict[str, object]], path: Path) -> None:
    raw = _rows_for(rows, "raw_token_score")
    n = [int(r["n"]) for r in raw]
    token = [float(r["selected_token_likelihood_mean"]) for r in raw]
    utility = [float(r["real_utility_mean"]) for r in raw]
    fig, ax1 = plt.subplots(figsize=(7.0, 4.2))
    ax1.plot(n, token, marker="o", color="#2d6cdf", label="selected token likelihood")
    ax1.set_xscale("log", base=2)
    ax1.set_xlabel("N candidates")
    ax1.set_ylabel("internal token score", color="#2d6cdf")
    ax1.tick_params(axis="y", labelcolor="#2d6cdf")
    ax2 = ax1.twinx()
    ax2.plot(n, utility, marker="s", color="#c0392b", label="real utility")
    ax2.set_ylabel("real utility after decoding", color="#c0392b")
    ax2.tick_params(axis="y", labelcolor="#c0392b")
    ax1.set_title("Token-likelihood physical aliasing")
    ax1.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_repair(rows: list[dict[str, object]], path: Path) -> None:
    methods = [
        ("raw_token_score", "raw", "#c0392b"),
        ("codebook_uncertainty", "codebook uncertainty", "#8e44ad"),
        ("decode_consistency", "decode consistency", "#16a085"),
        ("token_to_real_calibration", "pilot calibration", "#d68910"),
        ("combined_repair", "combined repair", "#1f7a3a"),
        ("oracle_real_utility", "oracle", "#111111"),
    ]
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    for method, label, color in methods:
        method_rows = _rows_for(rows, method)
        if not method_rows:
            continue
        ax.plot(
            [int(r["n"]) for r in method_rows],
            [float(r["real_utility_mean"]) for r in method_rows],
            marker="o",
            label=label,
            color=color,
        )
    ax.set_xscale("log", base=2)
    ax.set_xlabel("N candidates")
    ax.set_ylabel("selected real utility")
    ax.set_title("Token-specific repairs recover the selected tail")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_bottleneck(rows: list[dict[str, object]], path: Path) -> None:
    fig, ax1 = plt.subplots(figsize=(7.0, 4.2))
    k = [int(r["codebook_size"]) for r in rows]
    collision = [float(r["codebook_collision_rate"]) for r in rows]
    raw64 = [float(r["raw_real_utility_n64"]) for r in rows]
    repair64 = [float(r["combined_real_utility_n64"]) for r in rows]
    ax1.plot(k, collision, marker="o", color="#7f8c8d", label="collision rate")
    ax1.set_xlabel("codebook size")
    ax1.set_ylabel("collision rate")
    ax1.grid(alpha=0.25)
    ax2 = ax1.twinx()
    ax2.plot(k, raw64, marker="s", color="#c0392b", label="raw N=64")
    ax2.plot(k, repair64, marker="^", color="#1f7a3a", label="repair N=64")
    ax2.set_ylabel("real utility")
    ax1.set_title("Codebook bottleneck stress")
    lines = ax1.lines + ax2.lines
    ax1.legend(lines, [line.get_label() for line in lines], fontsize=8, loc="center right")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_validity(table: dict[str, np.ndarray], path: Path) -> None:
    kinds = ["valid", "alias", "rare_good", "bad_low"]
    metrics = ["collision_violation", "teleport_violation", "hidden_mode_error"]
    data = np.array(
        [
            [float(table[m][table["kind"] == kind].mean()) for m in metrics]
            for kind in kinds
        ]
    )
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    x = np.arange(len(kinds))
    width = 0.24
    colors = ["#34495e", "#d68910", "#8e44ad"]
    for i, metric in enumerate(metrics):
        ax.bar(x + (i - 1) * width, data[:, i], width=width, label=metric.replace("_", " "), color=colors[i])
    ax.set_xticks(x)
    ax.set_xticklabels(kinds)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("diagnostic rate/error")
    ax.set_title("Decode and physical-validity diagnostics")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_exact_law(validation: dict[str, object], path: Path) -> None:
    rows = validation["rows"]
    n = [int(r["n"]) for r in rows]  # type: ignore[index]
    exact = [float(r["exact"]) for r in rows]  # type: ignore[index]
    mc = [float(r["monte_carlo"]) for r in rows]  # type: ignore[index]
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.plot(n, exact, marker="o", label="exact law", color="#2d6cdf")
    ax.scatter(n, mc, label="Monte Carlo", color="#c0392b", zorder=3)
    ax.set_xscale("log", base=2)
    ax.set_xlabel("N candidates")
    ax.set_ylabel("expected selected utility")
    ax.set_title("Exact finite law validation")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_alias_atlas(table: dict[str, np.ndarray], path: Path) -> None:
    token_ids = sorted(int(t) for t in np.unique(table["token_id"]))
    alias = [float(table["alias_probability"][table["token_id"] == t].mean()) for t in token_ids]
    selected = np.zeros(len(token_ids))
    high = table["raw_score"] >= np.quantile(table["raw_score"], 0.9)
    for i, token_id in enumerate(token_ids):
        selected[i] = float(((table["token_id"] == token_id) & high).mean())
    fig, ax1 = plt.subplots(figsize=(7.2, 4.2))
    x = np.arange(len(token_ids))
    ax1.bar(x, alias, color="#7f8c8d", label="alias probability")
    ax1.set_xticks(x)
    ax1.set_xticklabels([str(t) for t in token_ids])
    ax1.set_xlabel("token id")
    ax1.set_ylabel("alias probability")
    ax2 = ax1.twinx()
    ax2.plot(x, selected, marker="o", color="#c0392b", label="top-tail share")
    ax2.set_ylabel("share of top-score tail")
    ax1.set_title("Alias atlas: codebook cells exploited by the tail")
    lines = ax1.patches[:1] + ax2.lines
    labels = ["alias probability", "top-tail share"]
    ax1.legend(lines, labels, fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)

