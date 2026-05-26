"""Edge-case tests for ratios and trends."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from finstmt import data, ratios as ratios_mod, trends


def test_cagr_needs_two_points():
    assert np.isnan(trends.cagr(pd.Series([100.0], index=[2023])))


def test_cagr_nan_for_non_positive_start():
    assert np.isnan(trends.cagr(pd.Series([0.0, 100.0], index=[2022, 2023])))
    assert np.isnan(trends.cagr(pd.Series([-50.0, 100.0], index=[2022, 2023])))


def test_zero_revenue_does_not_blow_up():
    df = data.synthetic_statements(seed=0)
    df.loc[df.index[0], "revenue"] = 0.0
    r = ratios_mod.compute_ratios(df)
    assert np.isnan(r.loc[df.index[0], "net_margin"])


def test_missing_columns_become_nan():
    df = pd.DataFrame({"revenue": [1000.0], "net_income": [100.0]}, index=[2023])
    finalized = data._finalize(df)
    # Columns the source lacked are present but NaN.
    assert np.isnan(finalized.loc[2023, "total_assets"])
    # A ratio needing a missing column is NaN, not an error.
    r = ratios_mod.compute_ratios(finalized)
    assert np.isnan(r.loc[2023, "return_on_assets"])
