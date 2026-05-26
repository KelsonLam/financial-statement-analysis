"""DuPont decomposition: why is return on equity what it is?

Return on equity is a single number that hides three very different stories. The
DuPont identity splits it into the parts that drive it:

    ROE = net margin x asset turnover x equity multiplier
        = (net income / revenue)
          x (revenue / total assets)
          x (total assets / total equity)

Two companies can post the same ROE for opposite reasons: one through fat
margins, another through heavy leverage. The decomposition makes that visible,
and a high ROE driven mostly by the equity multiplier is a quieter way of saying
"this return is borrowed."
"""

from __future__ import annotations

import pandas as pd

from .ratios import _safe_div


def dupont(df: pd.DataFrame) -> pd.DataFrame:
    """Year-indexed DuPont decomposition of return on equity."""
    out = pd.DataFrame(index=df.index)
    out["net_margin"] = _safe_div(df["net_income"], df["revenue"])
    out["asset_turnover"] = _safe_div(df["revenue"], df["total_assets"])
    out["equity_multiplier"] = _safe_div(df["total_assets"], df["total_equity"])
    out["roe"] = out["net_margin"] * out["asset_turnover"] * out["equity_multiplier"]
    return out
