"""Command line entry point: analyze a company's financial statements.

Examples
--------
Analyze the ticker in config.yaml (Apple by default)::

    python scripts/analyze_financials.py

Analyze a different company and save the charts::

    python scripts/analyze_financials.py --ticker MSFT --save-plots

Run on bundled synthetic statements with no network::

    python scripts/analyze_financials.py --synthetic
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from finstmt import data, ratios as ratios_mod, analysis, trends, plotting


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze a company's financial statements.")
    p.add_argument("--config", default=str(Path(__file__).resolve().parents[1] / "config.yaml"))
    p.add_argument("--ticker", help="Override the ticker.")
    p.add_argument("--synthetic", action="store_true", help="Use bundled synthetic statements.")
    p.add_argument("--save-plots", action="store_true", help="Write charts to results/.")
    return p.parse_args()


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    ticker = args.ticker or cfg["ticker"]

    if args.synthetic:
        print("Using synthetic statements.")
        df = data.synthetic_statements()
        label = "synthetic company"
    else:
        print(f"Loading financial statements for {ticker} ...")
        df = data.from_yfinance(ticker)
        label = ticker

    ratios = ratios_mod.compute_ratios(df)

    print(f"\nFinancial summary: {label}")
    print("=" * 50)

    print("\nGrowth (CAGR over the period):")
    for k, v in trends.growth_summary(df).items():
        name = k.replace("_cagr", "").replace("_", " ")
        print(f"  {name:<18} {v * 100:6.1f}%" if pd.notna(v) else f"  {name:<18}   n/a")

    print("\nRatios by year:")
    print(ratios_mod.format_ratios(ratios).to_string())

    print("\nRisk flags:")
    for flag in analysis.flag_risks(df, ratios, cfg.get("thresholds")):
        print(f"  - {flag}")

    if args.save_plots:
        f1 = plotting.plot_revenue_profit(df, f"Revenue and net income: {label}")
        f2 = plotting.plot_margins(ratios, f"Profitability margins: {label}")
        f3 = plotting.plot_key_ratios(ratios, f"Liquidity and leverage: {label}")
        for fig, name in [(f1, "revenue_profit"), (f2, "margins"), (f3, "key_ratios")]:
            out = plotting.save_figure(fig, f"results/{name}.png")
            print(f"Saved {out}")


if __name__ == "__main__":
    main()
