"""The ratios that turn raw statements into a read on the business.

Grouped the way an analyst thinks about them:

    Profitability  how much of each dollar of sales (or assets, or equity) ends
                   up as profit
    Liquidity      can the company cover its short-term bills
    Leverage       how much it leans on debt, and whether it can service it
    Cash           is the accounting profit backed by real cash

Every ratio is computed across all available years at once and returned as a
tidy table indexed by year.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _safe_div(a: pd.Series, b: pd.Series) -> pd.Series:
    return a / b.replace(0, np.nan)


def compute_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """Return a year-indexed table of the headline ratios."""
    r = pd.DataFrame(index=df.index)

    # Profitability
    r["gross_margin"] = _safe_div(df["gross_profit"], df["revenue"])
    r["operating_margin"] = _safe_div(df["operating_income"], df["revenue"])
    r["net_margin"] = _safe_div(df["net_income"], df["revenue"])
    r["return_on_assets"] = _safe_div(df["net_income"], df["total_assets"])
    r["return_on_equity"] = _safe_div(df["net_income"], df["total_equity"])

    # Liquidity
    r["current_ratio"] = _safe_div(df["current_assets"], df["current_liabilities"])
    r["quick_ratio"] = _safe_div(
        df["current_assets"] - df["inventory"], df["current_liabilities"]
    )
    r["cash_ratio"] = _safe_div(df["cash"], df["current_liabilities"])

    # Leverage
    r["debt_to_equity"] = _safe_div(df["total_debt"], df["total_equity"])
    r["debt_to_assets"] = _safe_div(df["total_debt"], df["total_assets"])
    r["interest_coverage"] = _safe_div(
        df["operating_income"], df["interest_expense"]
    )

    # Cash quality
    r["cash_conversion"] = _safe_div(df["operating_cash_flow"], df["net_income"])
    r["fcf_margin"] = _safe_div(df["free_cash_flow"], df["revenue"])

    return r


PERCENT_RATIOS = {
    "gross_margin", "operating_margin", "net_margin",
    "return_on_assets", "return_on_equity", "fcf_margin", "debt_to_assets",
}


def format_ratios(ratios: pd.DataFrame) -> pd.DataFrame:
    """A display copy with percentages shown as percentages."""
    shown = ratios.copy()
    for col in shown.columns:
        if col in PERCENT_RATIOS:
            shown[col] = (shown[col] * 100).round(1)
        else:
            shown[col] = shown[col].round(2)
    return shown
