# Apple Inc. (AAPL) — DCF Valuation: Executive Summary

**Valuation date:** August 12, 2026 | **Method:** 5-Year Unlevered FCFF DCF, Gordon Growth terminal value
**Companion file:** `Financial_Statement_Analysis_DCF.xlsx`

---

## 1. Headline Result

| Metric | Value |
|---|---|
| Current share price | $301.58 |
| DCF-implied share price (base case) | ~$132 |
| Implied upside / (downside) | ~(56%) |
| Enterprise Value | ~$2.02T |
| Equity Value | ~$1.98T |
| WACC | 9.47% |
| Terminal growth rate (g) | 2.5% |

*(All figures pull live from the workbook; re-run the model after any assumption change and update this table.)*

## 2. Historical Snapshot (FY2021 → FY2025)

- Revenue grew from $365.8B to $416.2B (a ~3.3% 4-year CAGR), with FY2023 a rare down year (-2.8%) followed by reacceleration in FY2024/FY2025.
- Gross margin expanded from 41.8% to 46.9%; operating margin from 29.8% to 32.0%, driven by Services (now ~26% of revenue) growing faster than hardware.
- Apple runs a structurally **negative** cash conversion cycle (approximately -70 days in FY2025): suppliers effectively finance Apple's inventory and receivables through extended payables terms.
- Free cash flow was $98.8B in FY2025, funding $96.7B of buybacks and $15.4B of dividends.

## 3. Forecast & Valuation Approach

- **Revenue growth:** tapers from 8% (Year 1) to 4% (Year 5), reflecting a services mix-shift and an assumed AI-driven upgrade cycle moderating toward long-run trend growth.
- **Operating margin:** expands from 32.5% to 34.0%, continuing the FY2021–FY2025 trend.
- **Cash tax rate:** 16.0%, in line with Apple's FY2021/FY2022/FY2023/FY2025 effective rate (excludes the FY2024 one-off EU State Aid charge).
- **WACC:** 9.47% — Cost of equity of 9.65% (CAPM: Rf 4.25% + β 1.08 × ERP 5.0%) blended with an after-tax cost of debt of ~1.28%, weighted at ~98%/2% equity/debt given Apple's very light leverage relative to its market cap.
- **Terminal value:** Gordon Growth at g = 2.5%, roughly long-run nominal GDP growth.

## 4. Key Takeaway

Under these base-case, intentionally conservative assumptions, the DCF's intrinsic value estimate sits well below Apple's current trading price. This is a common outcome when valuing mega-cap "compounders" on a standalone unlevered-FCFF basis: a large share of Apple's market value reflects continued aggressive buybacks (~$97–100B/year, shrinking share count ~3–4%/year), which compound EPS-per-share growth beyond what enterprise-level FCFF captures, plus a quality/scarcity premium the market assigns to Apple's balance sheet, ecosystem, and capital-return consistency.

The `Sensitivity_Analysis` tab shows just how much this conclusion depends on the WACC/growth spread: implied value ranges from roughly $120 (WACC 9.5%, g 2.0%) to roughly $254 (WACC 7.5%, g 4.0%) — still below the current price at every combination in the specified grid, but the point estimate should be read as the center of a wide range, not a precise target.

## 5. Caveats & Next Steps

- This is an educational/illustrative model, **not investment advice**. Verify every hardcoded (blue) input against Apple's latest 10-K/10-Q before relying on it.
- Apple does not separately disclose "interest expense" on its income statement; the $1.5B estimate used for cost of debt is a documented approximation — refine it if you have access to the debt-note detail in the 10-K.
- Consider supplementing this DCF with a relative-valuation cross-check (P/E, P/FCF vs. peers) and a levered/equity-FCF approach that explicitly models the buyback program, since a large part of AAPL's equity story runs through share-count reduction rather than enterprise cash-flow growth alone.
- Refresh cadence: update `Raw_Data` each quarter (or at minimum annually, after the 10-K) using `aapl_dcf_data_puller.py` (yfinance) as a starting point, then re-run recalculation.

---
*Sources: Apple Inc. FY2025 Form 10-K (SEC EDGAR, CIK 0000320193); StockAnalysis.com (data provider: Fiscal.ai), retrieved Aug 12, 2026.*
