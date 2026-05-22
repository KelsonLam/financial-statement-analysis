"""Charts: the revenue and profit story, the margin story, and the ratio story.

Matplotlib only. Each function returns the Figure.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot_revenue_profit(df, title="Revenue and net income"):
    """Revenue bars with net income overlaid, by year."""
    df = df.sort_index()
    years = df.index.astype(str)
    x = np.arange(len(years))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x, df["revenue"], color="tab:blue", alpha=0.7, label="Revenue")
    ax.plot(x, df["net_income"], color="tab:orange", marker="o",
            linewidth=2, label="Net income")
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.set_ylabel("Amount")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def plot_margins(ratios, title="Profitability margins"):
    """Gross, operating, and net margin over time."""
    ratios = ratios.sort_index()
    years = ratios.index.astype(str)
    fig, ax = plt.subplots(figsize=(10, 5))
    for col, label in [("gross_margin", "Gross"),
                       ("operating_margin", "Operating"),
                       ("net_margin", "Net")]:
        ax.plot(years, ratios[col] * 100, marker="o", label=label)
    ax.set_ylabel("Margin (%)")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_key_ratios(ratios, title="Liquidity and leverage"):
    """Current ratio and debt-to-equity over time, on twin axes."""
    ratios = ratios.sort_index()
    years = ratios.index.astype(str)
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(years, ratios["current_ratio"], color="tab:green",
             marker="o", label="Current ratio")
    ax1.set_ylabel("Current ratio", color="tab:green")
    ax1.tick_params(axis="y", labelcolor="tab:green")
    ax2 = ax1.twinx()
    ax2.plot(years, ratios["debt_to_equity"], color="tab:red",
             marker="s", label="Debt-to-equity")
    ax2.set_ylabel("Debt-to-equity", color="tab:red")
    ax2.tick_params(axis="y", labelcolor="tab:red")
    ax1.set_title(title)
    ax1.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def save_figure(fig, path: Path | str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    return path
