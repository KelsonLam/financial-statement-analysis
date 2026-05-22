"""Financial statement analysis: read a company's numbers and judge its health.

The flow mirrors how an analyst actually reads a company: pull the income
statement, balance sheet, and cash flow; line up several years; compute the
ratios that matter for profitability, liquidity, and leverage; and then turn
those into plain-language insights and risk flags.

Modules:

    data       load statements (yfinance) into one canonical yearly table
    ratios     profitability, liquidity, leverage, and efficiency ratios
    trends     year-over-year growth and multi-year CAGR
    analysis   a readable summary plus rule-of-thumb risk flags
    plotting   revenue and profit trends, margin and ratio charts

Every ratio is computed from a canonical table, so the analysis code never
depends on a data vendor's exact column names.
"""

__version__ = "0.1.0"
