import io
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import yfinance as yf

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DCF Valuation | Equity Research",
    page_icon="▣",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# STYLING (same green system)
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:wght@400;500;600;700&display=swap');

.stApp { background:#f7f8f6; color:#17221d; }
.block-container { max-width:1180px; padding-top:2.8rem; padding-bottom:4rem; }
header { background:transparent !important; }
#MainMenu, footer { visibility:hidden; }

.brand-bar {
  display:flex; justify-content:space-between; align-items:center;
  padding-bottom:18px; margin-bottom:28px; border-bottom:1px solid #dfe5e1;
}
.brand-name { font-size:15px; font-weight:700; letter-spacing:1px; color:#17221d; }
.brand-name span { color:#2f8053; }
.brand-meta, .section-meta, .sidebar-caption {
  font-family:'DM Mono',monospace; font-size:9px; letter-spacing:1px;
  color:#7c8982; text-transform:uppercase;
}
.eyebrow {
  font-family:'DM Mono',monospace; font-size:9px; letter-spacing:1.5px;
  color:#2f8053; text-transform:uppercase; margin-bottom:10px;
}
.page-title {
  font-size:38px; line-height:1.1; letter-spacing:-1.7px;
  font-weight:700; margin:0; color:#17221d;
}
.page-subtitle {
  font-size:13px; line-height:1.7; color:#68756e;
  max-width:820px; margin-top:12px; margin-bottom:8px;
}
.section-header {
  display:flex; justify-content:space-between; align-items:end;
  margin-top:36px; margin-bottom:16px;
  border-bottom:1px solid #dfe5e1; padding-bottom:12px;
}
.section-title { font-size:17px; font-weight:600; letter-spacing:-.3px; color:#17221d; }

.kpi-card, .analysis-card {
  background:#fff; border:1px solid #d5ded8; padding:18px 20px;
}
.kpi-card { min-height:112px; }
.kpi-label, .analysis-number {
  font-family:'DM Mono',monospace; font-size:9px; letter-spacing:1px;
  color:#7c8982; text-transform:uppercase;
}
.kpi-value {
  font-family:'DM Mono',monospace; font-size:23px; font-weight:500;
  color:#17221d; margin-top:12px;
}
.kpi-note {
  font-family:'DM Mono',monospace; font-size:9px; color:#2f8053; margin-top:5px;
}
.analysis-title { font-size:15px; font-weight:600; margin-top:14px; color:#17221d; }
.analysis-text { font-size:11px; line-height:1.7; color:#68756e; margin-top:7px; }

.risk-low { color:#2f8053; font-weight:700; }
.risk-moderate { color:#8a6d1d; font-weight:700; }
.risk-elevated { color:#9a5a20; font-weight:700; }
.risk-high { color:#9a3434; font-weight:700; }

section[data-testid="stSidebar"] {
  background:#edf2ee; border-right:1px solid #dfe5e1;
}
.sidebar-brand {
  font-size:15px; font-weight:700; letter-spacing:1px;
  color:#17221d; margin-bottom:3px;
}
.sidebar-brand span { color:#2f8053; }
.sidebar-section {
  font-family:'DM Mono',monospace; font-size:9px; letter-spacing:1.2px;
  color:#2f8053; text-transform:uppercase; margin-top:20px; margin-bottom:4px;
}

.stNumberInput label, .stTextInput label, .stSelectbox label, .stSlider label {
  font-size:11px !important; color:#536159 !important;
}
.stNumberInput input {
  font-family:'DM Mono',monospace !important; font-size:11px !important;
}

.stButton > button {
  width:100%; border-radius:4px; border:1px solid #17221d;
  background:#17221d; color:#fff; font-size:11px; font-weight:600;
}
.stButton > button:hover { border-color:#2f8053; background:#2f8053; }
.stDownloadButton > button {
  width:100%; border-radius:4px; border:1px solid #2f8053;
  background:transparent; color:#2f8053; font-size:10px; font-weight:600;
}
.stDownloadButton > button:hover { background:#2f8053; color:#fff; }

.stTabs [data-baseweb="tab-list"] { gap:0; border-bottom:1px solid #d5ded8; }
.stTabs [data-baseweb="tab"] { font-size:10px; color:#6e7b74; padding:12px 18px; }
.stTabs [aria-selected="true"] { color:#2f8053 !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color:#2f8053 !important; }

[data-testid="stDataFrame"] { border:1px solid #d5ded8; }

.app-footer {
  margin-top:55px; padding-top:18px; border-top:1px solid #dfe5e1;
  display:flex; justify-content:space-between;
  font-family:'DM Mono',monospace; font-size:8px; color:#849089;
  text-transform:uppercase; letter-spacing:.7px;
}

@media (prefers-color-scheme: dark) {
  .stApp { background:#111613; color:#e8eee9; }
  .brand-bar, .section-header, .app-footer { border-color:#29332d; }
  .brand-name, .page-title, .section-title, .kpi-value, .analysis-title, .sidebar-brand { color:#e8eee9; }
  .brand-meta, .page-subtitle, .section-meta, .kpi-label, .analysis-text { color:#9aa89f; }
  .kpi-card, .analysis-card { background:#171d19; border-color:#303b34; }
  section[data-testid="stSidebar"] { background:#171d19; border-color:#29332d; }
  .stTabs [data-baseweb="tab-list"], [data-testid="stDataFrame"] { border-color:#303b34; }
  .stTabs [data-baseweb="tab"] { color:#9aa89f; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# CORE FUNCTIONS
# ============================================================

def extract_line_item(df, candidate_keys):
    for key in candidate_keys:
        if key in df.index:
            return df.loc[key]
    return pd.Series(np.nan, index=df.columns if df is not None and not df.empty else [])


def kpi_card(label, value, note):
    return f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-note">{note}</div>
    </div>
    """


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_financials(ticker_symbol: str):
    ticker = yf.Ticker(ticker_symbol)
    inc_stmt = ticker.financials
    bal_sheet = ticker.balance_sheet
    cash_flow = ticker.cashflow

    if inc_stmt.empty or bal_sheet.empty or cash_flow.empty:
        return None

    # Market data
    try:
        fast = ticker.fast_info
        current_price = float(fast.get("last_price") or fast.get("lastPrice") or 0)
        market_cap = float(fast.get("market_cap") or fast.get("marketCap") or 0)
        shares_out = float(fast.get("shares") or 0)
    except Exception:
        current_price = market_cap = shares_out = 0

    try:
        info = ticker.info if isinstance(ticker.info, dict) else {}
        beta = info.get("beta") or 1.10
        if not beta or pd.isna(beta):
            beta = 1.10
        company_name = info.get("longName") or info.get("shortName") or ticker_symbol
    except Exception:
        beta = 1.10
        company_name = ticker_symbol

    return {
        "inc_stmt": inc_stmt,
        "bal_sheet": bal_sheet,
        "cash_flow": cash_flow,
        "current_price": current_price,
        "market_cap": market_cap,
        "shares_out": shares_out,
        "beta": float(beta),
        "company_name": company_name,
    }


def build_historical(inc_stmt, bal_sheet, cash_flow):
    rev = extract_line_item(inc_stmt, ["Total Revenue", "Operating Revenue", "Revenue"]).iloc[::-1]
    ebit = extract_line_item(inc_stmt, ["EBIT", "Operating Income", "Operating Income Loss"]).iloc[::-1]
    net_income = extract_line_item(
        inc_stmt, ["Net Income", "Net Income Common Stockholders", "Net Income Including Noncontrolling Interests"]
    ).iloc[::-1]
    pretax_income = extract_line_item(inc_stmt, ["Pretax Income", "Pretax Income Loss"]).iloc[::-1]
    tax_expense = extract_line_item(inc_stmt, ["Tax Provision", "Tax Expense"]).iloc[::-1]
    capex = extract_line_item(
        cash_flow, ["Capital Expenditure", "Capital Expenditures", "Capital Expenditure Reported"]
    ).iloc[::-1].abs()
    ocf = extract_line_item(
        cash_flow,
        ["Operating Cash Flow", "Total Cash From Operating Activities", "Cash Flow From Continuing Operating Activities"],
    ).iloc[::-1]
    da = extract_line_item(
        cash_flow, ["Depreciation And Amortization", "Depreciation", "Depreciation And Amortization In Cash Flow"]
    ).iloc[::-1].abs()
    accounts_receivable = extract_line_item(
        bal_sheet, ["Accounts Receivable", "Receivables", "Net Receivables", "Accounts Receivable Net"]
    ).iloc[::-1]
    inventory = extract_line_item(bal_sheet, ["Inventory", "Inventories", "Inventory Net"]).iloc[::-1]
    accounts_payable = extract_line_item(
        bal_sheet, ["Accounts Payable", "Payables", "Accounts Payable And Other Current Liabilities"]
    ).iloc[::-1]

    hist_df = pd.DataFrame({
        "Revenue": rev,
        "EBIT": ebit,
        "Net Income": net_income,
        "Pretax Income": pretax_income,
        "Tax Expense": tax_expense,
        "Op Cash Flow": ocf,
        "CapEx": capex,
        "D&A": da,
        "Accounts Receivable": accounts_receivable,
        "Inventory": inventory,
        "Accounts Payable": accounts_payable,
    })
    hist_df = hist_df.dropna(how="all")
    for col in hist_df.columns:
        hist_df[col] = pd.to_numeric(hist_df[col], errors="coerce")

    hist_df["NWC"] = (
        hist_df["Accounts Receivable"].fillna(0)
        + hist_df["Inventory"].fillna(0)
        - hist_df["Accounts Payable"].fillna(0)
    )
    hist_df["Change in NWC"] = hist_df["NWC"].diff()
    hist_df["FCF"] = hist_df["Op Cash Flow"] - hist_df["CapEx"]
    hist_df["Revenue Growth (%)"] = hist_df["Revenue"].pct_change() * 100
    hist_df["EBIT Margin (%)"] = (hist_df["EBIT"] / hist_df["Revenue"]) * 100
    hist_df["FCF Margin (%)"] = (hist_df["FCF"] / hist_df["Revenue"]) * 100
    hist_df["D&A % Revenue"] = hist_df["D&A"] / hist_df["Revenue"]
    hist_df["CapEx % Revenue"] = hist_df["CapEx"] / hist_df["Revenue"]
    hist_df["AR % Revenue"] = hist_df["Accounts Receivable"] / hist_df["Revenue"]
    hist_df["Inventory % Revenue"] = hist_df["Inventory"] / hist_df["Revenue"]
    hist_df["AP % Revenue"] = hist_df["Accounts Payable"] / hist_df["Revenue"]
    hist_df["Effective Tax Rate"] = np.where(
        hist_df["Pretax Income"] > 0,
        hist_df["Tax Expense"] / hist_df["Pretax Income"],
        np.nan,
    )
    hist_df = hist_df.replace([np.inf, -np.inf], np.nan)
    return hist_df


def get_balance_items(bal_sheet, inc_stmt):
    total_cash_series = extract_line_item(
        bal_sheet,
        ["Cash Cash Equivalents And Short Term Investments", "Cash And Cash Equivalents", "Cash Financial"],
    )
    total_debt_series = extract_line_item(
        bal_sheet, ["Total Debt", "Total Debt Net Minority Interest", "Long Term Debt And Capital Lease Obligation"]
    )
    total_cash = (
        total_cash_series.iloc[0]
        if len(total_cash_series) > 0 and pd.notna(total_cash_series.iloc[0])
        else 0
    )
    total_debt = (
        total_debt_series.iloc[0]
        if len(total_debt_series) > 0 and pd.notna(total_debt_series.iloc[0])
        else 0
    )
    interest_expense = extract_line_item(
        inc_stmt, ["Interest Expense Non Operating", "Interest Expense", "Interest Expense Non-Operating"]
    ).iloc[::-1].abs()
    return total_cash, total_debt, interest_expense


def compute_wacc(hist_df, market_cap, total_debt, beta, interest_expense, risk_free_rate, erp):
    valid_tax = hist_df["Effective Tax Rate"].replace([np.inf, -np.inf], np.nan).dropna()
    valid_tax = valid_tax[(valid_tax >= 0) & (valid_tax <= 0.50)]
    tax_rate = float(valid_tax.median()) if len(valid_tax) > 0 else 0.18

    if (
        len(interest_expense) > 0
        and total_debt > 0
        and pd.notna(interest_expense.iloc[-1])
        and interest_expense.iloc[-1] > 0
    ):
        cost_of_debt = min(max(float(interest_expense.iloc[-1] / total_debt), 0.02), 0.10)
    else:
        cost_of_debt = 0.045

    cost_of_equity = risk_free_rate + (beta * erp)
    v = market_cap + total_debt
    w_e = market_cap / v if v > 0 else 1.0
    w_d = total_debt / v if v > 0 else 0.0
    wacc = (w_e * cost_of_equity) + (w_d * cost_of_debt * (1 - tax_rate))
    return {
        "tax_rate": tax_rate,
        "cost_of_debt": cost_of_debt,
        "cost_of_equity": cost_of_equity,
        "wacc": wacc,
        "w_e": w_e,
        "w_d": w_d,
    }


def run_dcf(hist_df, wacc_inputs, total_cash, total_debt, shares_out, current_price, scenarios):
    tax_rate = wacc_inputs["tax_rate"]
    wacc = wacc_inputs["wacc"]

    latest_ebit_margin = hist_df["EBIT Margin (%)"].iloc[-1] / 100
    if pd.isna(latest_ebit_margin):
        latest_ebit_margin = 0.20

    def median_or(series, fallback):
        s = series.replace([np.inf, -np.inf], np.nan).dropna()
        return float(s.median()) if len(s) else fallback

    historical_da_pct = median_or(hist_df["D&A % Revenue"], 0.03)
    historical_capex_pct = median_or(hist_df["CapEx % Revenue"], 0.04)
    historical_ar_pct = median_or(hist_df["AR % Revenue"], 0.05)
    historical_inventory_pct = median_or(hist_df["Inventory % Revenue"], 0.03)
    historical_ap_pct = median_or(hist_df["AP % Revenue"], 0.05)

    base_rev = hist_df["Revenue"].iloc[-1]
    if pd.isna(base_rev) or base_rev <= 0:
        return None, None

    dcf_results = {}
    proj_detail = {}

    for case, params in scenarios.items():
        proj_years = 5
        forecast_growth = [
            max(params["growth"] + (params["growth_step"] * i), params["terminal_g"])
            for i in range(proj_years)
        ]
        forecast_rev = []
        previous_revenue = base_rev
        for g in forecast_growth:
            previous_revenue = previous_revenue * (1 + g)
            forecast_rev.append(previous_revenue)

        forecast_ebit_margin = [
            max(params["ebit_margin"] + (params["margin_step"] * i), 0.05) for i in range(proj_years)
        ]
        forecast_ebit = [r * m for r, m in zip(forecast_rev, forecast_ebit_margin)]
        forecast_nopat = [e * (1 - tax_rate) for e in forecast_ebit]
        forecast_da = [r * historical_da_pct for r in forecast_rev]
        forecast_capex = [r * historical_capex_pct for r in forecast_rev]
        forecast_ar = [r * historical_ar_pct for r in forecast_rev]
        forecast_inventory = [r * historical_inventory_pct for r in forecast_rev]
        forecast_ap = [r * historical_ap_pct for r in forecast_rev]
        forecast_nwc = [ar + inv - ap for ar, inv, ap in zip(forecast_ar, forecast_inventory, forecast_ap)]

        forecast_change_nwc = []
        previous_nwc = hist_df["NWC"].iloc[-1] if pd.notna(hist_df["NWC"].iloc[-1]) else 0
        for nwc in forecast_nwc:
            forecast_change_nwc.append(nwc - previous_nwc)
            previous_nwc = nwc

        forecast_fcff = [
            nopat + da - capex - chg
            for nopat, da, capex, chg in zip(forecast_nopat, forecast_da, forecast_capex, forecast_change_nwc)
        ]

        discounts = [(1 + wacc) ** i for i in range(1, proj_years + 1)]
        pv_fcff = sum(fcff / d for fcff, d in zip(forecast_fcff, discounts))

        terminal_fcff = forecast_fcff[-1] * (1 + params["terminal_g"])
        terminal_val = terminal_fcff / (wacc - params["terminal_g"]) if wacc > params["terminal_g"] else 0
        pv_terminal_val = terminal_val / ((1 + wacc) ** proj_years)

        enterprise_value = pv_fcff + pv_terminal_val
        equity_value = enterprise_value + total_cash - total_debt
        implied_price = equity_value / shares_out if shares_out > 0 else 0

        dcf_results[case] = {
            "Implied Share Price ($)": round(implied_price, 2),
            "Upside/Downside (%)": round(((implied_price - current_price) / current_price) * 100, 2)
            if current_price
            else 0,
            "Enterprise Value ($B)": round(enterprise_value / 1e9, 2),
        }
        proj_detail[case] = {
            "Revenue": forecast_rev,
            "EBIT": forecast_ebit,
            "FCFF": forecast_fcff,
            "Growth": forecast_growth,
            "EBIT Margin": forecast_ebit_margin,
        }

    return pd.DataFrame(dcf_results).T, proj_detail


def sensitivity_matrix(hist_df, wacc_inputs, total_cash, total_debt, shares_out, scenarios, base_case_key="Base Case"):
    tax_rate = wacc_inputs["tax_rate"]
    wacc = wacc_inputs["wacc"]
    params = scenarios[base_case_key]
    base_rev = hist_df["Revenue"].iloc[-1]

    def median_or(series, fallback):
        s = series.replace([np.inf, -np.inf], np.nan).dropna()
        return float(s.median()) if len(s) else fallback

    historical_da_pct = median_or(hist_df["D&A % Revenue"], 0.03)
    historical_capex_pct = median_or(hist_df["CapEx % Revenue"], 0.04)
    historical_ar_pct = median_or(hist_df["AR % Revenue"], 0.05)
    historical_inventory_pct = median_or(hist_df["Inventory % Revenue"], 0.03)
    historical_ap_pct = median_or(hist_df["AP % Revenue"], 0.05)

    base_forecast_growth = [
        max(params["growth"] + (params["growth_step"] * i), params["terminal_g"]) for i in range(5)
    ]
    base_forecast_revenue = []
    prev = base_rev
    for g in base_forecast_growth:
        prev = prev * (1 + g)
        base_forecast_revenue.append(prev)

    base_forecast_margin = [
        max(params["ebit_margin"] + (params["margin_step"] * i), 0.05) for i in range(5)
    ]
    base_forecast_ebit = [r * m for r, m in zip(base_forecast_revenue, base_forecast_margin)]
    base_forecast_nopat = [e * (1 - tax_rate) for e in base_forecast_ebit]
    base_forecast_da = [r * historical_da_pct for r in base_forecast_revenue]
    base_forecast_capex = [r * historical_capex_pct for r in base_forecast_revenue]
    base_forecast_ar = [r * historical_ar_pct for r in base_forecast_revenue]
    base_forecast_inventory = [r * historical_inventory_pct for r in base_forecast_revenue]
    base_forecast_ap = [r * historical_ap_pct for r in base_forecast_revenue]
    base_forecast_nwc = [
        ar + inv - ap for ar, inv, ap in zip(base_forecast_ar, base_forecast_inventory, base_forecast_ap)
    ]
    base_forecast_change_nwc = []
    prev_nwc = hist_df["NWC"].iloc[-1] if pd.notna(hist_df["NWC"].iloc[-1]) else 0
    for nwc in base_forecast_nwc:
        base_forecast_change_nwc.append(nwc - prev_nwc)
        prev_nwc = nwc
    base_forecast_fcff = [
        nopat + da - capex - chg
        for nopat, da, capex, chg in zip(
            base_forecast_nopat, base_forecast_da, base_forecast_capex, base_forecast_change_nwc
        )
    ]
    base_fcf_5 = base_forecast_fcff[-1]

    wacc_range = np.linspace(wacc - 0.01, wacc + 0.01, 5)
    g_range = np.linspace(0.015, 0.035, 5)
    sens_matrix = np.zeros((len(wacc_range), len(g_range)))

    for i, w in enumerate(wacc_range):
        for j, g in enumerate(g_range):
            if w <= g:
                sens_matrix[i, j] = np.nan
                continue
            pv_f = sum(base_forecast_fcff[k - 1] / ((1 + w) ** k) for k in range(1, 6))
            tv = (base_fcf_5 * (1 + g)) / (w - g)
            pv_tv = tv / ((1 + w) ** 5)
            ev = pv_f + pv_tv
            eq_val = ev + total_cash - total_debt
            sens_matrix[i, j] = eq_val / shares_out if shares_out > 0 else np.nan

    sens_df = pd.DataFrame(
        sens_matrix.round(2),
        index=[f"WACC: {w:.2%}" for w in wacc_range],
        columns=[f"g: {g:.2%}" for g in g_range],
    )
    return sens_df


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
<div class="brand-bar">
  <div class="brand-name">Prustide Bangandozou<span>.</span></div>
  <div class="brand-meta">Finance · Analytics · Technology</div>
</div>
<div class="eyebrow">EQUITY RESEARCH · DCF VALUATION · FUNDAMENTAL ANALYSIS</div>
<div class="page-title">DCF Valuation Model</div>
<div class="page-subtitle">
  Pull live financial statements, compute historical drivers, build a 5-year FCFF forecast,
  and run Bear / Base / Bull DCF scenarios with WACC and terminal-growth sensitivity.
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    """
<div class="sidebar-brand">DCF<span>.</span></div>
<div class="sidebar-caption">Equity Valuation Platform</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.markdown('<div class="sidebar-section">Ticker</div>', unsafe_allow_html=True)
ticker_input = st.sidebar.text_input("Ticker Symbol", value="AAPL").upper().strip()
run_btn = st.sidebar.button("Run Analysis", type="primary")

st.sidebar.markdown('<div class="sidebar-section">WACC Assumptions</div>', unsafe_allow_html=True)
risk_free_rate = st.sidebar.number_input("Risk-Free Rate", 0.01, 0.10, 0.0425, 0.0025, format="%.4f")
erp = st.sidebar.number_input("Equity Risk Premium", 0.02, 0.10, 0.05, 0.005, format="%.3f")

st.sidebar.markdown('<div class="sidebar-section">Scenario Overrides (Base Case)</div>', unsafe_allow_html=True)
base_growth = st.sidebar.slider("Base Revenue Growth (Y1)", 0.02, 0.25, 0.09, 0.01)
base_terminal_g = st.sidebar.slider("Terminal Growth", 0.015, 0.04, 0.025, 0.005)

# ============================================================
# MAIN LOGIC
# ============================================================

if not run_btn and "dcf_data" not in st.session_state:
    st.info("Enter a ticker in the sidebar and click **Run Analysis**.")
    st.stop()

if run_btn:
    with st.spinner(f"Fetching financials for {ticker_input}..."):
        raw = fetch_financials(ticker_input)
        if raw is None:
            st.error(f"Could not retrieve financial statements for **{ticker_input}**. Check the ticker and try again.")
            st.stop()
        st.session_state["dcf_data"] = raw
        st.session_state["ticker"] = ticker_input

data = st.session_state.get("dcf_data")
ticker_symbol = st.session_state.get("ticker", ticker_input)

if data is None:
    st.stop()

hist_df = build_historical(data["inc_stmt"], data["bal_sheet"], data["cash_flow"])
if hist_df.empty or hist_df["Revenue"].dropna().empty:
    st.error("Insufficient historical data to build the model.")
    st.stop()

total_cash, total_debt, interest_expense = get_balance_items(data["bal_sheet"], data["inc_stmt"])
current_price = data["current_price"]
market_cap = data["market_cap"]
shares_out = data["shares_out"]
beta = data["beta"]
company_name = data["company_name"]

wacc_inputs = compute_wacc(
    hist_df, market_cap, total_debt, beta, interest_expense, risk_free_rate, erp
)

latest_ebit_margin = hist_df["EBIT Margin (%)"].iloc[-1] / 100
if pd.isna(latest_ebit_margin):
    latest_ebit_margin = 0.20

scenarios = {
    "Bear Case": {
        "growth": max(base_growth - 0.04, 0.02),
        "growth_step": -0.0025,
        "ebit_margin": latest_ebit_margin * 0.90,
        "margin_step": -0.0025,
        "terminal_g": max(base_terminal_g - 0.005, 0.015),
    },
    "Base Case": {
        "growth": base_growth,
        "growth_step": -0.0075,
        "ebit_margin": latest_ebit_margin,
        "margin_step": 0.0010,
        "terminal_g": base_terminal_g,
    },
    "Bull Case": {
        "growth": base_growth + 0.05,
        "growth_step": -0.0100,
        "ebit_margin": latest_ebit_margin * 1.10,
        "margin_step": 0.0025,
        "terminal_g": min(base_terminal_g + 0.005, 0.035),
    },
}

dcf_summary, proj_detail = run_dcf(
    hist_df, wacc_inputs, total_cash, total_debt, shares_out, current_price, scenarios
)
sens_df = sensitivity_matrix(
    hist_df, wacc_inputs, total_cash, total_debt, shares_out, scenarios
)

# ============================================================
# KPI SNAPSHOT
# ============================================================

st.markdown(
    f"""
<div class="section-header">
  <div class="section-title">{company_name} ({ticker_symbol})</div>
  <div class="section-meta">Live market inputs</div>
</div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(kpi_card("Share Price", f"${current_price:.2f}", "Last price"), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("Market Cap", f"${market_cap/1e9:.1f}B", "Equity value"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("WACC", f"{wacc_inputs['wacc']:.2%}", "Discount rate"), unsafe_allow_html=True)
with c4:
    base_price = dcf_summary.loc["Base Case", "Implied Share Price ($)"] if dcf_summary is not None else 0
    st.markdown(kpi_card("Base DCF Price", f"${base_price:.2f}", "Implied value"), unsafe_allow_html=True)
with c5:
    upside = dcf_summary.loc["Base Case", "Upside/Downside (%)"] if dcf_summary is not None else 0
    st.markdown(kpi_card("Upside / Downside", f"{upside:+.1f}%", "vs market"), unsafe_allow_html=True)

st.caption(
    "Educational DCF model using Yahoo Finance data. Not investment advice. "
    "Line-item mapping can vary by company reporting structure."
)

# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Dashboard",
    "Historical",
    "DCF Scenarios",
    "Sensitivity",
    "Assumptions",
])

# ── Tab 1: Dashboard ───────────────────────────────────────
with tab1:
    st.markdown(
        """
<div class="section-header">
  <div class="section-title">Valuation Dashboard</div>
  <div class="section-meta">Executive view</div>
</div>
""",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1.5])
    with left:
        if dcf_summary is not None:
            for case in ["Bear Case", "Base Case", "Bull Case"]:
                row = dcf_summary.loc[case]
                css = "risk-high" if case == "Bear Case" else ("risk-low" if case == "Bull Case" else "risk-moderate")
                st.markdown(
                    f"""
                    <div class="analysis-card" style="margin-bottom:12px;">
                      <div class="analysis-number">{case.upper()}</div>
                      <div class="kpi-value">${row['Implied Share Price ($)']:.2f}</div>
                      <div class="analysis-title"><span class="{css}">{row['Upside/Downside (%)']:+.1f}%</span></div>
                      <div class="analysis-text">EV ${row['Enterprise Value ($B)']:.1f}B</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with right:
        fig, ax = plt.subplots(figsize=(8, 4.2))
        plot_data = hist_df[["Revenue", "FCF"]].dropna(how="all") / 1e9
        x = np.arange(len(plot_data))
        width = 0.35
        ax.bar(x - width / 2, plot_data["Revenue"].fillna(0), width, label="Revenue", color="#2f8053")
        ax.bar(x + width / 2, plot_data["FCF"].fillna(0), width, label="FCF", color="#17221d")
        ax.set_xticks(x)
        ax.set_xticklabels([str(d)[:4] for d in plot_data.index], rotation=0)
        ax.set_ylabel("$ Billions")
        ax.set_title(f"{ticker_symbol}: Historical Revenue & FCF")
        ax.legend()
        ax.grid(axis="y", alpha=0.2)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)

# ── Tab 2: Historical ──────────────────────────────────────
with tab2:
    st.markdown(
        """
<div class="section-header">
  <div class="section-title">Historical Performance</div>
  <div class="section-meta">Last reported years</div>
</div>
""",
        unsafe_allow_html=True,
    )

    hist_display = (
        hist_df[["Revenue", "EBIT", "Net Income", "Op Cash Flow", "CapEx", "D&A", "NWC", "Change in NWC", "FCF"]]
        / 1e9
    ).round(2)
    hist_display.columns = [f"{c} ($B)" for c in hist_display.columns]
    st.dataframe(hist_display, use_container_width=True)

    st.markdown(
        """
<div class="section-header">
  <div class="section-title">Operating Drivers</div>
  <div class="section-meta">Margins & ratios</div>
</div>
""",
        unsafe_allow_html=True,
    )
    driver_display = hist_df[
        [
            "Revenue Growth (%)",
            "EBIT Margin (%)",
            "FCF Margin (%)",
            "D&A % Revenue",
            "CapEx % Revenue",
            "AR % Revenue",
            "Inventory % Revenue",
            "AP % Revenue",
            "Effective Tax Rate",
        ]
    ].copy()
    for col in ["D&A % Revenue", "CapEx % Revenue", "AR % Revenue", "Inventory % Revenue", "AP % Revenue", "Effective Tax Rate"]:
        driver_display[col] = driver_display[col] * 100
    st.dataframe(driver_display.round(2), use_container_width=True)

# ── Tab 3: DCF Scenarios ───────────────────────────────────
with tab3:
    st.markdown(
        """
<div class="section-header">
  <div class="section-title">DCF Scenario Summary</div>
  <div class="section-meta">Bear · Base · Bull</div>
</div>
""",
        unsafe_allow_html=True,
    )
    if dcf_summary is not None:
        st.dataframe(
            dcf_summary.style.format({
                "Implied Share Price ($)": "${:.2f}",
                "Upside/Downside (%)": "{:+.1f}%",
                "Enterprise Value ($B)": "${:.1f}B",
            }),
            use_container_width=True,
        )

        if proj_detail:
            st.markdown(
                """
<div class="section-header">
  <div class="section-title">Base Case Projection</div>
  <div class="section-meta">5-year FCFF build</div>
</div>
""",
                unsafe_allow_html=True,
            )
            base = proj_detail["Base Case"]
            years = [f"Y{i+1}" for i in range(5)]
            proj_df = pd.DataFrame({
                "Year": years,
                "Revenue ($B)": [r / 1e9 for r in base["Revenue"]],
                "EBIT ($B)": [e / 1e9 for e in base["EBIT"]],
                "FCFF ($B)": [f / 1e9 for f in base["FCFF"]],
                "Growth": base["Growth"],
                "EBIT Margin": base["EBIT Margin"],
            })
            st.dataframe(
                proj_df.style.format({
                    "Revenue ($B)": "{:.2f}",
                    "EBIT ($B)": "{:.2f}",
                    "FCFF ($B)": "{:.2f}",
                    "Growth": "{:.1%}",
                    "EBIT Margin": "{:.1%}",
                }),
                use_container_width=True,
                hide_index=True,
            )

# ── Tab 4: Sensitivity ─────────────────────────────────────
with tab4:
    st.markdown(
        """
<div class="section-header">
  <div class="section-title">Price Sensitivity</div>
  <div class="section-meta">WACC vs Terminal Growth</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.dataframe(sens_df, use_container_width=True)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.heatmap(
        sens_df,
        annot=True,
        fmt=".2f",
        cmap="YlGnBu",
        ax=ax,
        cbar_kws={"label": "Implied Share Price ($)"},
    )
    ax.set_title(f"{ticker_symbol}: DCF Price Sensitivity (WACC vs g)")
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)

# ── Tab 5: Assumptions ─────────────────────────────────────
with tab5:
    st.markdown(
        """
<div class="section-header">
  <div class="section-title">Model Assumptions</div>
  <div class="section-meta">Transparency</div>
</div>
""",
        unsafe_allow_html=True,
    )
    a1, a2 = st.columns(2)
    with a1:
        st.markdown(
            f"""
            <div class="analysis-card">
              <div class="analysis-number">CAPITAL STRUCTURE</div>
              <div class="analysis-text">
                Market Cap: ${market_cap/1e9:.2f}B<br>
                Total Cash: ${total_cash/1e9:.2f}B<br>
                Total Debt: ${total_debt/1e9:.2f}B<br>
                Shares Out: {shares_out/1e9:.2f}B<br>
                Beta: {beta:.2f}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with a2:
        st.markdown(
            f"""
            <div class="analysis-card">
              <div class="analysis-number">WACC BUILD</div>
              <div class="analysis-text">
                Risk-Free Rate: {risk_free_rate:.2%}<br>
                Equity Risk Premium: {erp:.2%}<br>
                Cost of Equity: {wacc_inputs['cost_of_equity']:.2%}<br>
                Cost of Debt: {wacc_inputs['cost_of_debt']:.2%}<br>
                Tax Rate: {wacc_inputs['tax_rate']:.2%}<br>
                WACC: {wacc_inputs['wacc']:.2%}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
<div class="section-header">
  <div class="section-title">Scenario Parameters</div>
  <div class="section-meta">Growth & margin paths</div>
</div>
""",
        unsafe_allow_html=True,
    )
    scen_rows = []
    for name, p in scenarios.items():
        scen_rows.append({
            "Scenario": name,
            "Y1 Growth": p["growth"],
            "Growth Step": p["growth_step"],
            "EBIT Margin": p["ebit_margin"],
            "Margin Step": p["margin_step"],
            "Terminal g": p["terminal_g"],
        })
    scen_df = pd.DataFrame(scen_rows)
    st.dataframe(
        scen_df.style.format({
            "Y1 Growth": "{:.1%}",
            "Growth Step": "{:.2%}",
            "EBIT Margin": "{:.1%}",
            "Margin Step": "{:.2%}",
            "Terminal g": "{:.1%}",
        }),
        use_container_width=True,
        hide_index=True,
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="app-footer">
  <span>Prustide Bangandozou · FINANCE &amp; ANALYTICS</span>
  <span>DCF · PYTHON · STREAMLIT · EQUITY RESEARCH</span>
</div>
""",
    unsafe_allow_html=True,
)