"""Tests for the canonical schema, ratio math, trends, and risk flags.

Uses hand-built statements with known answers plus the synthetic generator. No
network needed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from finstmt import data, ratios as ratios_mod, trends, analysis


def _toy() -> pd.DataFrame:
    df = pd.DataFrame({
        "revenue": [1000.0, 1200.0],
        "gross_profit": [400.0, 480.0],
        "operating_income": [200.0, 240.0],
        "net_income": [100.0, 120.0],
        "interest_expense": [20.0, 20.0],
        "total_assets": [2000.0, 2200.0],
        "total_equity": [1000.0, 1100.0],
        "current_assets": [600.0, 700.0],
        "current_liabilities": [300.0, 350.0],
        "total_debt": [500.0, 520.0],
        "cash": [200.0, 250.0],
        "inventory": [100.0, 120.0],
        "operating_cash_flow": [130.0, 150.0],
        "capex": [-50.0, -60.0],
    }, index=[2022, 2023])
    return data._finalize(df)


def test_synthetic_has_all_canonical_columns():
    df = data.synthetic_statements()
    for col in data.CANONICAL:
        assert col in df.columns
    assert "free_cash_flow" in df.columns


def test_known_ratios():
    df = _toy()
    r = ratios_mod.compute_ratios(df)
    # 2022: net margin 100/1000 = 0.10, ROE 100/1000 = 0.10
    assert r.loc[2022, "net_margin"] == pytest.approx(0.10)
    assert r.loc[2022, "return_on_equity"] == pytest.approx(0.10)
    # current ratio 600/300 = 2.0, quick (600-100)/300 = 1.6667
    assert r.loc[2022, "current_ratio"] == pytest.approx(2.0)
    assert r.loc[2022, "quick_ratio"] == pytest.approx(500 / 300)
    # debt-to-equity 500/1000 = 0.5, interest coverage 200/20 = 10
    assert r.loc[2022, "debt_to_equity"] == pytest.approx(0.5)
    assert r.loc[2022, "interest_coverage"] == pytest.approx(10.0)


def test_free_cash_flow_is_ocf_plus_capex():
    df = _toy()
    assert df.loc[2022, "free_cash_flow"] == pytest.approx(130.0 - 50.0)


def test_cagr_matches_definition():
    s = pd.Series([100.0, 121.0], index=[2021, 2023])  # two years apart
    # (121/100)^(1/1) - 1 over one step in the series (len-1 = 1)
    assert trends.cagr(s) == pytest.approx(0.21)


def test_safe_div_handles_zero():
    df = _toy()
    df.loc[2022, "current_liabilities"] = 0.0
    r = ratios_mod.compute_ratios(df)
    assert np.isnan(r.loc[2022, "current_ratio"])


def test_risk_flags_fire_on_weak_company():
    df = _toy()
    # Make it weak: tiny current assets, big debt, negative net income.
    df.loc[2023, "current_assets"] = 100.0
    df.loc[2023, "current_liabilities"] = 400.0
    df.loc[2023, "total_debt"] = 5000.0
    df.loc[2023, "net_income"] = -50.0
    r = ratios_mod.compute_ratios(df)
    flags = analysis.flag_risks(df, r)
    joined = " ".join(flags).lower()
    assert "liquidity" in joined
    assert "leverage" in joined
    assert "profitab" in joined


def test_healthy_company_has_no_flags():
    # A deterministically healthy company: improving margins, strong liquidity,
    # low leverage, and positive free cash flow.
    df = data._finalize(pd.DataFrame({
        "revenue": [1000.0, 1100.0, 1210.0],
        "gross_profit": [400.0, 460.0, 520.0],
        "operating_income": [200.0, 240.0, 290.0],
        "net_income": [100.0, 121.0, 150.0],          # margin rises 10% -> 12.4%
        "interest_expense": [10.0, 10.0, 10.0],        # coverage of 20x or more
        "total_assets": [1500.0, 1600.0, 1700.0],
        "total_equity": [1000.0, 1100.0, 1250.0],
        "current_assets": [600.0, 650.0, 700.0],
        "current_liabilities": [300.0, 300.0, 300.0],  # current ratio >= 2.0
        "total_debt": [300.0, 300.0, 300.0],           # debt-to-equity ~0.3
        "cash": [250.0, 280.0, 320.0],
        "inventory": [100.0, 110.0, 120.0],
        "operating_cash_flow": [120.0, 140.0, 170.0],
        "capex": [-40.0, -45.0, -50.0],                # positive free cash flow
    }, index=[2021, 2022, 2023]))
    r = ratios_mod.compute_ratios(df)
    flags = analysis.flag_risks(df, r)
    assert any("No rule-of-thumb risk flags" in f for f in flags)
