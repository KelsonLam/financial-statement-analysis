"""Growth over time: year-over-year changes and multi-year CAGR.

A single year's ratios tell you the state of the business. The trend tells you
the direction, which is usually the more important question.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def yoy_growth(series: pd.Series) -> pd.Series:
    """Year-over-year percentage change, oldest to newest."""
    return series.sort_index().pct_change()


def cagr(series: pd.Series) -> float:
    """Compound annual growth rate from the first to the last period.

    Returns NaN if the series is too short or the start value is not positive.
    """
    s = series.sort_index().dropna()
    if len(s) < 2:
        return float("nan")
    start, end = s.iloc[0], s.iloc[-1]
    years = len(s) - 1
    if start <= 0 or end <= 0:
        return float("nan")
    return (end / start) ** (1.0 / years) - 1.0


def growth_summary(df: pd.DataFrame) -> dict[str, float]:
    """CAGR for the headline lines that people ask about first."""
    out = {}
    for field in ("revenue", "net_income", "operating_income", "free_cash_flow"):
        if field in df.columns:
            out[f"{field}_cagr"] = cagr(df[field])
    return out
