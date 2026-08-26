# DCF Valuation — Automated Equity Research

An automated Discounted Cash Flow (DCF) valuation model that pulls live financial statements from Yahoo Finance, builds a full historical financial picture, projects Bear/Base/Bull case cash flows, and outputs an implied share price with a WACC/growth sensitivity analysis. Available as both a standalone Python script (`financial_analysis_dcf.py`) and an interactive Streamlit dashboard (`dcfapp.py`).

---

## What it does

1. **Fetches live data** for any public ticker via `yfinance` — income statement, balance sheet, cash flow statement, current price, market cap, shares outstanding, and beta.
2. **Dynamically extracts line items** across different companies' reporting formats (e.g., "Total Revenue" vs. "Operating Revenue"), so the model works across tickers without manual remapping.
3. **Builds historical financials**: revenue growth, EBIT margin, free cash flow (FCF), net working capital (NWC) and its change, D&A %, CapEx %, and effective tax rate.
4. **Calculates WACC** from a CAPM cost of equity (risk-free rate + beta × equity risk premium), an implied cost of debt from interest expense, and market-value equity/debt weights.
5. **Projects 5-year Bear / Base / Bull case FCFF** (NOPAT + D&A − CapEx − Δ NWC) using each scenario's revenue growth, margin trajectory, and terminal growth rate.
6. **Discounts cash flows and terminal value** back to the present to get Enterprise Value → Equity Value → Implied Share Price, and compares it to the current market price.
7. **Runs a sensitivity matrix** of implied share price across a range of WACC and terminal growth assumptions.
8. **Visualizes results**: historical revenue/FCF bar chart and a WACC-vs-growth sensitivity heatmap.

---

## Project structure

```
.
├── financial_analysis_dcf.py   # Script — run analysis for one ticker, saves PNG chart
└── dcfapp.py                   # Streamlit dashboard — interactive, adjustable assumptions
```

No input files are required — both pull data live from Yahoo Finance at runtime.

---

## Installation

```bash
pip install yfinance pandas numpy matplotlib seaborn
pip install streamlit   # only needed for the dashboard (dcfapp.py)
```

---

## Usage

### Option A: Script

Edit the ticker at the bottom of the file (defaults to `"AAPL"`):

```python
run_financial_analysis("AAPL")
```

Then run:

```bash
python financial_analysis_dcf.py
```

**Output:**
- Console: available GL line items, historical performance table, historical operating drivers, dynamic WACC inputs, Bear/Base/Bull DCF summary, and the sensitivity matrix
- `<TICKER>_dcf_valuation.png` — a two-panel chart (historical Revenue & FCF, and the WACC-vs-growth sensitivity heatmap)

### Option B: Interactive dashboard

```bash
streamlit run dcfapp.py
```

From the sidebar you can:
- Enter any ticker symbol and click **Run Analysis**
- Adjust WACC assumptions (risk-free rate, equity risk premium)
- Override Base Case scenario inputs (Year-1 revenue growth, terminal growth rate) live

The dashboard has five tabs: **Dashboard** (KPIs and valuation snapshot), **Historical** (financials and operating drivers), **DCF Scenarios** (Bear/Base/Bull implied share price and enterprise value), **Sensitivity** (WACC × terminal growth heatmap), and **Assumptions** (a transparent view of every input driving the model).

---

## Key assumptions & methodology

| Input | Source |
|---|---|
| Risk-free rate | Configurable (default 4.25%) |
| Equity risk premium | Configurable (default 5.0%) |
| Beta | Pulled live from Yahoo Finance (`info['beta']`), falls back to 1.10 |
| Cost of debt | Implied from latest interest expense ÷ total debt, bounded 2%–10%, falls back to 4.5% |
| Tax rate | Median of historical effective tax rates (0%–50% range), falls back to 18% |
| D&A, CapEx, AR, Inventory, AP | Forecast as a % of revenue, using historical medians (with sensible fallbacks if a company doesn't report a line item) |
| Terminal growth | Scenario-specific (2.0% Bear / 2.5% Base / 3.0% Bull), adjustable in the dashboard |

Enterprise Value = PV of 5-year FCFF + PV of Terminal Value. Equity Value = Enterprise Value + Cash − Debt. Implied Share Price = Equity Value ÷ Shares Outstanding.

---

## Notes

- This is an educational/portfolio equity-research model, not investment advice — all forecasts depend on the scenario assumptions and simplified operating-driver relationships built into the model.
- Because it relies on `yfinance`, results depend on Yahoo Finance's data availability and formatting for a given ticker; the `extract_line_item` helper is designed to gracefully handle missing or differently-labeled line items.
- The script and dashboard share the same core valuation logic, so the automated one-ticker run and the interactive tool produce consistent numbers.
