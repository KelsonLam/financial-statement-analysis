"""Tests for the DuPont decomposition."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from finstmt import data
from finstmt.dupont import dupont


def _toy():
    df = pd.DataFrame({
        "revenue": [1000.0], "gross_profit": [400.0], "operating_income": [200.0],
        "net_income": [120.0], "interest_expense": [10.0], "total_assets": [2000.0],
        "total_equity": [800.0], "current_assets": [600.0],
        "current_liabilities": [300.0], "total_debt": [500.0], "cash": [200.0],
        "inventory": [100.0], "operating_cash_flow": [150.0], "capex": [-40.0],
    }, index=[2023])
    return data._finalize(df)


def test_components_multiply_to_roe():
    d = dupont(_toy())
    # ROE should equal net_income / total_equity = 120 / 800 = 0.15.
    assert d.loc[2023, "roe"] == pytest.approx(0.15)
    product = (d.loc[2023, "net_margin"]
               * d.loc[2023, "asset_turnover"]
               * d.loc[2023, "equity_multiplier"])
    assert product == pytest.approx(0.15)


def test_individual_components():
    d = dupont(_toy())
    assert d.loc[2023, "net_margin"] == pytest.approx(0.12)        # 120/1000
    assert d.loc[2023, "asset_turnover"] == pytest.approx(0.5)     # 1000/2000
    assert d.loc[2023, "equity_multiplier"] == pytest.approx(2.5)  # 2000/800


def test_runs_on_synthetic():
    d = dupont(data.synthetic_statements())
    assert "roe" in d.columns
    assert len(d) == 5
