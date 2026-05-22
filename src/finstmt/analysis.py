"""Turn the ratios and trends into plain-language insights and risk flags.

The flags are deliberately rule-of-thumb. A current ratio below 1 or debt to
equity above 2 is worth a second look, but what counts as healthy depends
heavily on the industry, so these are conversation starters, not verdicts.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import trends

DEFAULT_THRESHOLDS = {
    "min_current_ratio": 1.0,
    "max_debt_to_equity": 2.0,
    "min_interest_coverage": 3.0,
    "min_net_margin": 0.0,
}


def latest_snapshot(ratios: pd.DataFrame) -> pd.Series:
    """The most recent year's ratios."""
    return ratios.sort_index().iloc[-1]


def flag_risks(
    df: pd.DataFrame, ratios: pd.DataFrame, thresholds: dict | None = None
) -> list[str]:
    """Return a list of human-readable risk flags for the latest year."""
    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    latest = latest_snapshot(ratios)
    year = ratios.sort_index().index[-1]
    flags: list[str] = []

    cur = latest.get("current_ratio")
    if pd.notna(cur) and cur < t["min_current_ratio"]:
        flags.append(
            f"Liquidity: current ratio is {cur:.2f} in {year}, below "
            f"{t['min_current_ratio']:.2f}. Short-term obligations may be tight."
        )

    dte = latest.get("debt_to_equity")
    if pd.notna(dte) and dte > t["max_debt_to_equity"]:
        flags.append(
            f"Leverage: debt-to-equity is {dte:.2f}, above "
            f"{t['max_debt_to_equity']:.2f}. The balance sheet leans heavily on debt."
        )

    cov = latest.get("interest_coverage")
    if pd.notna(cov) and cov < t["min_interest_coverage"]:
        flags.append(
            f"Solvency: interest coverage is {cov:.2f}x, below "
            f"{t['min_interest_coverage']:.1f}x. Operating income barely covers interest."
        )

    nm = latest.get("net_margin")
    if pd.notna(nm) and nm < t["min_net_margin"]:
        flags.append(
            f"Profitability: net margin is {nm * 100:.1f}% in {year}. "
            "The company is not profitable on the bottom line."
        )

    # Trend-based flags
    net_margin = ratios["net_margin"].sort_index().dropna()
    if len(net_margin) >= 3 and net_margin.iloc[-1] < net_margin.iloc[0]:
        flags.append(
            "Trend: net margin has compressed over the period rather than expanded."
        )

    if "free_cash_flow" in df.columns:
        fcf = df["free_cash_flow"].sort_index().dropna()
        if len(fcf) and fcf.iloc[-1] < 0:
            flags.append(
                f"Cash: free cash flow was negative in {year}. The business "
                "consumed more cash than it produced after capital spending."
            )

    if not flags:
        flags.append("No rule-of-thumb risk flags triggered for the latest year.")
    return flags


def summarize(df: pd.DataFrame, ratios: pd.DataFrame) -> dict:
    """Bundle the headline numbers, latest ratios, and growth into one dict."""
    latest = latest_snapshot(ratios)
    return {
        "years": list(df.sort_index().index),
        "latest_year": int(df.sort_index().index[-1]),
        "growth": trends.growth_summary(df),
        "latest_ratios": latest.to_dict(),
    }
