"""Load financial statements into one canonical, vendor-agnostic table.

The rest of the project works on a single DataFrame indexed by fiscal year, with
one column per canonical line item (revenue, net_income, total_assets, and so
on). The yfinance loader maps that vendor's messy and changing row labels onto
this schema with a best-effort lookup, so the analysis code never has to know
what yfinance happens to call something this month.

A synthetic generator is included so the test suite and a first run need no
network.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Canonical line items the analysis expects (any missing one becomes NaN).
CANONICAL = [
    "revenue", "gross_profit", "operating_income", "net_income",
    "interest_expense", "total_assets", "total_equity",
    "current_assets", "current_liabilities", "total_debt",
    "cash", "inventory", "operating_cash_flow", "capex",
]

# Candidate yfinance labels for each canonical field, in order of preference.
_YF_LABELS = {
    "revenue": ["Total Revenue", "Operating Revenue"],
    "gross_profit": ["Gross Profit"],
    "operating_income": ["Operating Income", "EBIT"],
    "net_income": ["Net Income", "Net Income Common Stockholders"],
    "interest_expense": ["Interest Expense", "Interest Expense Non Operating"],
    "total_assets": ["Total Assets"],
    "total_equity": ["Stockholders Equity",
                     "Total Equity Gross Minority Interest"],
    "current_assets": ["Current Assets", "Total Current Assets"],
    "current_liabilities": ["Current Liabilities", "Total Current Liabilities"],
    "total_debt": ["Total Debt"],
    "cash": ["Cash And Cash Equivalents",
             "Cash Cash Equivalents And Short Term Investments"],
    "inventory": ["Inventory"],
    "operating_cash_flow": ["Operating Cash Flow",
                            "Total Cash From Operating Activities"],
    "capex": ["Capital Expenditure", "Capital Expenditures"],
}


def _pick(frame: pd.DataFrame, labels: list[str]) -> pd.Series | None:
    """Return the first matching row from a yfinance statement frame."""
    for label in labels:
        if label in frame.index:
            return frame.loc[label]
    return None


def from_yfinance(ticker: str) -> pd.DataFrame:
    """Build the canonical yearly table from yfinance statements."""
    import yfinance as yf

    t = yf.Ticker(ticker)
    income = t.income_stmt
    balance = t.balance_sheet
    cashflow = t.cashflow
    if income is None or income.empty:
        raise ValueError(f"No financial statements returned for {ticker}.")

    frames = {"income": income, "balance": balance, "cashflow": cashflow}
    source_for = {
        "revenue": "income", "gross_profit": "income",
        "operating_income": "income", "net_income": "income",
        "interest_expense": "income",
        "total_assets": "balance", "total_equity": "balance",
        "current_assets": "balance", "current_liabilities": "balance",
        "total_debt": "balance", "cash": "balance", "inventory": "balance",
        "operating_cash_flow": "cashflow", "capex": "cashflow",
    }

    columns = {}
    for field, labels in _YF_LABELS.items():
        frame = frames[source_for[field]]
        row = _pick(frame, labels) if frame is not None and not frame.empty else None
        columns[field] = row

    df = pd.DataFrame(columns)
    # yfinance columns are period-end timestamps; index by year, oldest first.
    df.index = pd.to_datetime(df.index).year
    df = df.sort_index()
    return _finalize(df)


def synthetic_statements(
    n_years: int = 5, start_year: int = 2020, seed: int = 42
) -> pd.DataFrame:
    """A plausible, healthy, growing company, for tests and offline runs."""
    rng = np.random.default_rng(seed)
    years = np.arange(start_year, start_year + n_years)

    revenue = 100_000.0 * np.cumprod(1 + rng.normal(0.10, 0.03, n_years))
    gross_profit = revenue * rng.uniform(0.38, 0.42, n_years)
    operating_income = revenue * rng.uniform(0.22, 0.27, n_years)
    net_income = operating_income * rng.uniform(0.74, 0.80, n_years)
    interest_expense = np.full(n_years, 3_000.0)
    total_assets = revenue * rng.uniform(1.5, 1.7, n_years)
    total_equity = total_assets * rng.uniform(0.42, 0.5, n_years)
    current_assets = total_assets * rng.uniform(0.30, 0.36, n_years)
    current_liabilities = current_assets * rng.uniform(0.7, 0.95, n_years)
    total_debt = total_assets * rng.uniform(0.25, 0.32, n_years)
    cash = current_assets * rng.uniform(0.4, 0.55, n_years)
    inventory = current_assets * rng.uniform(0.1, 0.18, n_years)
    operating_cash_flow = net_income * rng.uniform(1.05, 1.2, n_years)
    capex = -revenue * rng.uniform(0.05, 0.08, n_years)

    df = pd.DataFrame({
        "revenue": revenue, "gross_profit": gross_profit,
        "operating_income": operating_income, "net_income": net_income,
        "interest_expense": interest_expense, "total_assets": total_assets,
        "total_equity": total_equity, "current_assets": current_assets,
        "current_liabilities": current_liabilities, "total_debt": total_debt,
        "cash": cash, "inventory": inventory,
        "operating_cash_flow": operating_cash_flow, "capex": capex,
    }, index=years)
    return _finalize(df)


def _finalize(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure every canonical column exists and add derived free cash flow."""
    for col in CANONICAL:
        if col not in df.columns:
            df[col] = np.nan
    df = df[CANONICAL].astype(float)
    # Free cash flow = operating cash flow + capex (capex is stored negative).
    df["free_cash_flow"] = df["operating_cash_flow"] + df["capex"]
    df.index.name = "year"
    return df
