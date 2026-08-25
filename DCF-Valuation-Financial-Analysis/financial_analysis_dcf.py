import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set visual style
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'


def extract_line_item(df, candidate_keys):
    """Utility to safely match line items across different company reporting structures."""
    for key in candidate_keys:
        if key in df.index:
            return df.loc[key]

    print(f"Warning: Could not find any of these line items: {candidate_keys}")
    return pd.Series(np.nan, index=df.columns)


def run_financial_analysis(ticker_symbol=""):
    ticker_symbol = ticker_symbol.upper().strip()

    print("==================================================")
    print(f"=== Running Analysis for Ticker: {ticker_symbol} ===")
    print("==================================================")

    ticker = yf.Ticker(ticker_symbol)

    # 1. Fetch Historical Statements
    inc_stmt = ticker.financials
    bal_sheet = ticker.balance_sheet
    cash_flow = ticker.cashflow

    if inc_stmt.empty or bal_sheet.empty or cash_flow.empty:
        print(f"Error: Could not retrieve financial statements for {ticker_symbol}.")
        return

    # Debugging / transparency: show available Yahoo Finance line items
    print("\n--- Available Income Statement Rows ---")
    print(inc_stmt.index.tolist())

    print("\n--- Available Balance Sheet Rows ---")
    print(bal_sheet.index.tolist())

    print("\n--- Available Cash Flow Rows ---")
    print(cash_flow.index.tolist())

    # 2. Dynamic Financial Data Extraction

    rev = extract_line_item(
        inc_stmt,
        [
            'Total Revenue',
            'Operating Revenue',
            'Revenue'
        ]
    ).iloc[::-1]

    ebit = extract_line_item(
        inc_stmt,
        [
            'EBIT',
            'Operating Income',
            'Operating Income Loss'
        ]
    ).iloc[::-1]

    net_income = extract_line_item(
        inc_stmt,
        [
            'Net Income',
            'Net Income Common Stockholders',
            'Net Income Including Noncontrolling Interests'
        ]
    ).iloc[::-1]

    pretax_income = extract_line_item(
        inc_stmt,
        [
            'Pretax Income',
            'Pretax Income Loss'
        ]
    ).iloc[::-1]

    tax_expense = extract_line_item(
        inc_stmt,
        [
            'Tax Provision',
            'Tax Expense'
        ]
    ).iloc[::-1]

    capex = extract_line_item(
        cash_flow,
        [
            'Capital Expenditure',
            'Capital Expenditures',
            'Capital Expenditure Reported'
        ]
    ).iloc[::-1].abs()

    ocf = extract_line_item(
        cash_flow,
        [
            'Operating Cash Flow',
            'Total Cash From Operating Activities',
            'Cash Flow From Continuing Operating Activities'
        ]
    ).iloc[::-1]

    da = extract_line_item(
        cash_flow,
        [
            'Depreciation And Amortization',
            'Depreciation',
            'Depreciation And Amortization In Cash Flow'
        ]
    ).iloc[::-1].abs()

    # Balance Sheet
    accounts_receivable = extract_line_item(
        bal_sheet,
        [
            'Accounts Receivable',
            'Receivables',
            'Net Receivables',
            'Accounts Receivable Net'
        ]
    ).iloc[::-1]

    inventory = extract_line_item(
        bal_sheet,
        [
            'Inventory',
            'Inventories',
            'Inventory Net'
        ]
    ).iloc[::-1]

    accounts_payable = extract_line_item(
        bal_sheet,
        [
            'Accounts Payable',
            'Payables',
            'Accounts Payable And Other Current Liabilities'
        ]
    ).iloc[::-1]

    # Build Historical DataFrame
    hist_df = pd.DataFrame({
        'Revenue': rev,
        'EBIT': ebit,
        'Net Income': net_income,
        'Pretax Income': pretax_income,
        'Tax Expense': tax_expense,
        'Op Cash Flow': ocf,
        'CapEx': capex,
        'D&A': da,
        'Accounts Receivable': accounts_receivable,
        'Inventory': inventory,
        'Accounts Payable': accounts_payable
    })

    # Remove completely empty rows
    hist_df = hist_df.dropna(how='all')

    # Ensure financial data is numeric
    for column in hist_df.columns:
        hist_df[column] = pd.to_numeric(
            hist_df[column],
            errors='coerce'
        )

    # Calculate Historical Working Capital
    hist_df['NWC'] = (
        hist_df['Accounts Receivable'].fillna(0) +
        hist_df['Inventory'].fillna(0) -
        hist_df['Accounts Payable'].fillna(0)
    )

    hist_df['Change in NWC'] = hist_df['NWC'].diff()

    # Calculate Historical FCF
    hist_df['FCF'] = (
        hist_df['Op Cash Flow'] -
        hist_df['CapEx']
    )

    # Calculate Margins & Growth
    hist_df['Revenue Growth (%)'] = (
        hist_df['Revenue'].pct_change() * 100
    )

    hist_df['EBIT Margin (%)'] = (
        hist_df['EBIT'] /
        hist_df['Revenue']
    ) * 100

    hist_df['FCF Margin (%)'] = (
        hist_df['FCF'] /
        hist_df['Revenue']
    ) * 100

    # Additional Operating Drivers

    hist_df['D&A % Revenue'] = (
        hist_df['D&A'] /
        hist_df['Revenue']
    )

    hist_df['CapEx % Revenue'] = (
        hist_df['CapEx'] /
        hist_df['Revenue']
    )

    hist_df['AR % Revenue'] = (
        hist_df['Accounts Receivable'] /
        hist_df['Revenue']
    )

    hist_df['Inventory % Revenue'] = (
        hist_df['Inventory'] /
        hist_df['Revenue']
    )

    hist_df['AP % Revenue'] = (
        hist_df['Accounts Payable'] /
        hist_df['Revenue']
    )

    # Effective Tax Rate
    hist_df['Effective Tax Rate'] = np.where(
        hist_df['Pretax Income'] > 0,
        hist_df['Tax Expense'] /
        hist_df['Pretax Income'],
        np.nan
    )

    # Replace infinite values with NaN
    hist_df = hist_df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    print("\n--- Historical Performance (Last 4 Years) ---")

    historical_display = hist_df[[
        'Revenue',
        'EBIT',
        'Net Income',
        'Op Cash Flow',
        'CapEx',
        'D&A',
        'NWC',
        'Change in NWC',
        'FCF'
    ]] / 1e9

    historical_display = historical_display.round(2).rename(columns={
        'Revenue': 'Revenue ($B)',
        'EBIT': 'EBIT ($B)',
        'Net Income': 'Net Income ($B)',
        'Op Cash Flow': 'Op Cash Flow ($B)',
        'CapEx': 'CapEx ($B)',
        'D&A': 'D&A ($B)',
        'NWC': 'NWC ($B)',
        'Change in NWC': 'Change in NWC ($B)',
        'FCF': 'FCF ($B)'
    })

    print(historical_display)

    # Display Historical Operating Drivers
    print("\n--- Historical Operating Drivers ---")

    driver_display = hist_df[[
        'Revenue Growth (%)',
        'EBIT Margin (%)',
        'FCF Margin (%)',
        'D&A % Revenue',
        'CapEx % Revenue',
        'AR % Revenue',
        'Inventory % Revenue',
        'AP % Revenue',
        'Effective Tax Rate'
    ]].copy()

    driver_display['D&A % Revenue'] *= 100
    driver_display['CapEx % Revenue'] *= 100
    driver_display['AR % Revenue'] *= 100
    driver_display['Inventory % Revenue'] *= 100
    driver_display['AP % Revenue'] *= 100
    driver_display['Effective Tax Rate'] *= 100

    driver_display = driver_display.round(2)

    print(driver_display)

    # 3. Live Valuation Market Inputs using fast_info

    try:
        fast = ticker.fast_info

        current_price = fast['last_price']
        market_cap = fast['market_cap']
        shares_out = fast['shares']

    except Exception as e:
        print(f"Warning: Could not retrieve fast_info: {e}")
        return

    # Balance Sheet Items

    total_cash_series = extract_line_item(
        bal_sheet,
        [
            'Cash Cash Equivalents And Short Term Investments',
            'Cash And Cash Equivalents',
            'Cash Financial'
        ]
    )

    total_debt_series = extract_line_item(
        bal_sheet,
        [
            'Total Debt',
            'Total Debt Net Minority Interest',
            'Long Term Debt And Capital Lease Obligation'
        ]
    )

    total_cash = (
        total_cash_series.iloc[0]
        if len(total_cash_series) > 0 and
        pd.notna(total_cash_series.iloc[0])
        else 0
    )

    total_debt = (
        total_debt_series.iloc[0]
        if len(total_debt_series) > 0 and
        pd.notna(total_debt_series.iloc[0])
        else 0
    )

    # 4. WACC Parameters

    risk_free_rate = 0.0425
    erp = 0.050

    try:
        info = ticker.info

        beta = (
            info.get('beta', 1.10)
            if isinstance(info, dict)
            else 1.10
        )

        if not beta or pd.isna(beta):
            beta = 1.10

    except Exception:
        beta = 1.10

    # Normalize Historical Tax Rate
    valid_tax_rates = (
        hist_df['Effective Tax Rate']
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    # Remove unusual tax rates
    valid_tax_rates = valid_tax_rates[
        (valid_tax_rates >= 0) &
        (valid_tax_rates <= 0.50)
    ]

    if len(valid_tax_rates) > 0:
        tax_rate = valid_tax_rates.median()
    else:
        tax_rate = 0.18

    # Calculate Historical Cost of Debt
    interest_expense = extract_line_item(
        inc_stmt,
        [
            'Interest Expense Non Operating',
            'Interest Expense',
            'Interest Expense Non-Operating'
        ]
    ).iloc[::-1].abs()

    if (
        len(interest_expense) > 0 and
        total_debt > 0 and
        pd.notna(interest_expense.iloc[-1]) and
        interest_expense.iloc[-1] > 0
    ):
        latest_interest_expense = interest_expense.iloc[-1]

        cost_of_debt = (
            latest_interest_expense /
            total_debt
        )

        # Prevent extreme outliers
        cost_of_debt = min(
            max(cost_of_debt, 0.02),
            0.10
        )

    else:
        cost_of_debt = 0.045

    # Cost of Equity
    cost_of_equity = (
        risk_free_rate +
        (beta * erp)
    )

    # WACC
    v = market_cap + total_debt

    if v > 0:
        w_e = market_cap / v
        w_d = total_debt / v
    else:
        w_e = 1
        w_d = 0

    wacc = (
        (w_e * cost_of_equity) +
        (
            w_d *
            cost_of_debt *
            (1 - tax_rate)
        )
    )

    print("\n--- Dynamic Valuation Inputs ---")
    print(f"Current Stock Price : ${current_price:.2f}")
    print(f"Shares Outstanding  : {shares_out / 1e9:.2f} Billion")
    print(f"Market Cap          : ${market_cap / 1e9:.2f} Billion")
    print(f"Total Cash          : ${total_cash / 1e9:.2f} Billion")
    print(f"Total Debt          : ${total_debt / 1e9:.2f} Billion")
    print(f"Tax Rate            : {tax_rate:.2%}")
    print(f"Cost of Equity      : {cost_of_equity:.2%}")
    print(f"Cost of Debt        : {cost_of_debt:.2%}")
    print(f"Calculated WACC     : {wacc:.2%}")

    # 5. DCF Scenario Projections

    latest_ebit_margin = (
        hist_df['EBIT Margin (%)'].iloc[-1] / 100
    )

    # Historical operating drivers

    historical_da_pct = (
        hist_df['D&A % Revenue']
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
        .median()
    )

    historical_capex_pct = (
        hist_df['CapEx % Revenue']
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
        .median()
    )

    historical_ar_pct = (
        hist_df['AR % Revenue']
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
        .median()
    )

    historical_inventory_pct = (
        hist_df['Inventory % Revenue']
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
        .median()
    )

    historical_ap_pct = (
        hist_df['AP % Revenue']
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
        .median()
    )

    # Fallback assumptions if a company genuinely does not report
    # one of these line items.

    if pd.isna(historical_da_pct):
        historical_da_pct = 0.03

    if pd.isna(historical_capex_pct):
        historical_capex_pct = 0.04

    if pd.isna(historical_ar_pct):
        historical_ar_pct = 0.05

    if pd.isna(historical_inventory_pct):
        historical_inventory_pct = 0.03

    if pd.isna(historical_ap_pct):
        historical_ap_pct = 0.05

    # Scenario assumptions

    scenarios = {
        'Bear Case': {
            'growth': 0.05,
            'growth_step': -0.0025,
            'ebit_margin': latest_ebit_margin * 0.90,
            'margin_step': -0.0025,
            'terminal_g': 0.020
        },

        'Base Case': {
            'growth': 0.09,
            'growth_step': -0.0075,
            'ebit_margin': latest_ebit_margin,
            'margin_step': 0.0010,
            'terminal_g': 0.025
        },

        'Bull Case': {
            'growth': 0.14,
            'growth_step': -0.0100,
            'ebit_margin': latest_ebit_margin * 1.10,
            'margin_step': 0.0025,
            'terminal_g': 0.030
        }
    }

    base_rev = hist_df['Revenue'].iloc[-1]

    dcf_results = {}

    for case, params in scenarios.items():

        proj_years = 5

        # Revenue Forecast
        forecast_growth = [
            max(
                params['growth'] +
                (params['growth_step'] * i),
                params['terminal_g']
            )
            for i in range(proj_years)
        ]

        forecast_rev = []

        previous_revenue = base_rev

        for growth_rate in forecast_growth:

            next_revenue = (
                previous_revenue *
                (1 + growth_rate)
            )

            forecast_rev.append(
                next_revenue
            )

            previous_revenue = next_revenue

        # EBIT Forecast

        forecast_ebit_margin = [
            max(
                params['ebit_margin'] +
                (params['margin_step'] * i),
                0.05
            )
            for i in range(proj_years)
        ]

        forecast_ebit = [
            revenue * margin
            for revenue, margin in zip(
                forecast_rev,
                forecast_ebit_margin
            )
        ]

        # NOPAT

        forecast_nopat = [
            ebit * (1 - tax_rate)
            for ebit in forecast_ebit
        ]

        # D&A

        forecast_da = [
            revenue * historical_da_pct
            for revenue in forecast_rev
        ]

        # CapEx

        forecast_capex = [
            revenue * historical_capex_pct
            for revenue in forecast_rev
        ]

        # Accounts Receivable

        forecast_ar = [
            revenue * historical_ar_pct
            for revenue in forecast_rev
        ]

        # Inventory

        forecast_inventory = [
            revenue * historical_inventory_pct
            for revenue in forecast_rev
        ]

        # Accounts Payable

        forecast_ap = [
            revenue * historical_ap_pct
            for revenue in forecast_rev
        ]

        # Net Working Capital

        forecast_nwc = [
            ar + inventory - ap
            for ar, inventory, ap in zip(
                forecast_ar,
                forecast_inventory,
                forecast_ap
            )
        ]

        # Change in NWC

        forecast_change_nwc = []

        previous_nwc = hist_df['NWC'].iloc[-1]

        for nwc in forecast_nwc:

            change_nwc = (
                nwc -
                previous_nwc
            )

            forecast_change_nwc.append(
                change_nwc
            )

            previous_nwc = nwc

        # Proper FCFF Calculation
        #
        # FCFF = NOPAT + D&A - CapEx - Change in NWC

        forecast_fcff = [
            nopat +
            da -
            capex -
            change_nwc

            for nopat, da, capex, change_nwc
            in zip(
                forecast_nopat,
                forecast_da,
                forecast_capex,
                forecast_change_nwc
            )
        ]

        # Present Value of Forecasted FCFF

        discounts = [
            (1 + wacc) ** i
            for i in range(
                1,
                proj_years + 1
            )
        ]

        pv_fcff = sum([
            fcff / discount
            for fcff, discount
            in zip(
                forecast_fcff,
                discounts
            )
        ])

        # Terminal Value

        terminal_fcff = (
            forecast_fcff[-1] *
            (1 + params['terminal_g'])
        )

        terminal_val = (
            terminal_fcff /
            (wacc - params['terminal_g'])
        )

        pv_terminal_val = (
            terminal_val /
            ((1 + wacc) ** proj_years)
        )

        # Valuation Bridge

        enterprise_value = (
            pv_fcff +
            pv_terminal_val
        )

        equity_value = (
            enterprise_value +
            total_cash -
            total_debt
        )

        implied_price = (
            equity_value /
            shares_out
        )

        dcf_results[case] = {
            'Implied Share Price ($)': round(
                implied_price,
                2
            ),

            'Upside/Downside (%)': round(
                (
                    (implied_price - current_price) /
                    current_price
                ) * 100,
                2
            ),

            'Enterprise Value ($B)': round(
                enterprise_value / 1e9,
                2
            )
        }

    dcf_summary = pd.DataFrame(
        dcf_results
    ).T

    print("\n--- DCF Valuation Summary ---")
    print(dcf_summary)

    # 6. Sensitivity Analysis Matrix
    # WACC vs. Terminal Growth

    wacc_range = np.linspace(
        wacc - 0.01,
        wacc + 0.01,
        5
    )

    g_range = np.linspace(
        0.015,
        0.035,
        5
    )

    sens_matrix = np.zeros(
        (
            len(wacc_range),
            len(g_range)
        )
    )

    # Base Case assumptions

    base_growth = (
        scenarios['Base Case']['growth']
    )

    base_growth_step = (
        scenarios['Base Case']['growth_step']
    )

    base_margin = (
        scenarios['Base Case']['ebit_margin']
    )

    base_margin_step = (
        scenarios['Base Case']['margin_step']
    )

    # Base Case Revenue Forecast

    base_forecast_growth = [
        max(
            base_growth +
            (base_growth_step * i),
            scenarios['Base Case']['terminal_g']
        )
        for i in range(5)
    ]

    base_forecast_revenue = []

    previous_revenue = base_rev

    for growth_rate in base_forecast_growth:

        next_revenue = (
            previous_revenue *
            (1 + growth_rate)
        )

        base_forecast_revenue.append(
            next_revenue
        )

        previous_revenue = next_revenue

    # Base Case EBIT Margin

    base_forecast_margin = [
        max(
            base_margin +
            (base_margin_step * i),
            0.05
        )
        for i in range(5)
    ]

    base_forecast_ebit = [
        revenue * margin
        for revenue, margin in zip(
            base_forecast_revenue,
            base_forecast_margin
        )
    ]

    # Base Case NOPAT

    base_forecast_nopat = [
        ebit * (1 - tax_rate)
        for ebit in base_forecast_ebit
    ]

    # Base Case D&A

    base_forecast_da = [
        revenue * historical_da_pct
        for revenue in base_forecast_revenue
    ]

    # Base Case CapEx

    base_forecast_capex = [
        revenue * historical_capex_pct
        for revenue in base_forecast_revenue
    ]

    # Base Case Working Capital

    base_forecast_ar = [
        revenue * historical_ar_pct
        for revenue in base_forecast_revenue
    ]

    base_forecast_inventory = [
        revenue * historical_inventory_pct
        for revenue in base_forecast_revenue
    ]

    base_forecast_ap = [
        revenue * historical_ap_pct
        for revenue in base_forecast_revenue
    ]

    base_forecast_nwc = [
        ar +
        inventory -
        ap

        for ar, inventory, ap in zip(
            base_forecast_ar,
            base_forecast_inventory,
            base_forecast_ap
        )
    ]

    # Base Case Change in NWC

    base_forecast_change_nwc = []

    previous_nwc = hist_df['NWC'].iloc[-1]

    for nwc in base_forecast_nwc:

        change_nwc = (
            nwc -
            previous_nwc
        )

        base_forecast_change_nwc.append(
            change_nwc
        )

        previous_nwc = nwc

    # Base Case FCFF

    base_forecast_fcff = [
        nopat +
        da -
        capex -
        change_nwc

        for nopat, da, capex, change_nwc
        in zip(
            base_forecast_nopat,
            base_forecast_da,
            base_forecast_capex,
            base_forecast_change_nwc
        )
    ]

    base_fcf_5 = (
        base_forecast_fcff[-1]
    )

    # Sensitivity Matrix

    for i, w in enumerate(wacc_range):

        for j, g in enumerate(g_range):

            if w <= g:
                sens_matrix[i, j] = np.nan
                continue

            # PV of 5-Year FCFF

            pv_f = sum([
                base_forecast_fcff[k - 1] /
                ((1 + w) ** k)

                for k in range(1, 6)
            ])

            # Terminal Value

            tv = (
                base_fcf_5 *
                (1 + g)
            ) / (w - g)

            pv_tv = (
                tv /
                ((1 + w) ** 5)
            )

            # Enterprise Value

            ev = (
                pv_f +
                pv_tv
            )

            # Equity Value

            eq_val = (
                ev +
                total_cash -
                total_debt
            )

            # Implied Share Price

            sens_matrix[i, j] = (
                eq_val /
                shares_out
            )

    sens_df = pd.DataFrame(
        sens_matrix.round(2),

        index=[
            f"WACC: {w:.2%}"
            for w in wacc_range
        ],

        columns=[
            f"g: {g:.2%}"
            for g in g_range
        ]
    )

    # 7. Visualization

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(14, 5)
    )

    # Plot 1: Revenue vs FCF Historical

    plot_data = (
        hist_df[
            ['Revenue', 'FCF']
        ] / 1e9
    )

    plot_data.plot(
        kind='bar',
        ax=axes[0],
        color=[
            '#1f77b4',
            '#2ca02c'
        ]
    )

    axes[0].set_title(
        f"{ticker_symbol}: Historical Revenue & FCF ($ Billions)"
    )

    axes[0].set_xticklabels(
        [
            str(d)[:4]
            for d in hist_df.index
        ],
        rotation=0
    )

    axes[0].set_ylabel(
        "$ Billions"
    )

    # Plot 2: Sensitivity Heatmap

    sns.heatmap(
        sens_df,
        annot=True,
        fmt=".2f",
        cmap="YlGnBu",
        ax=axes[1],
        cbar_kws={
            'label': 'Implied Share Price ($)'
        }
    )

    axes[1].set_title(
        f"{ticker_symbol}: DCF Price Sensitivity (WACC vs. g)"
    )

    plt.tight_layout()

    chart_filename = (
        f"{ticker_symbol}_dcf_valuation.png"
    )

    plt.savefig(
        chart_filename,
        dpi=300
    )

    print(
        f"\nDashboard saved as '{chart_filename}'."
    )


# Test with Microsoft or NVIDIA or Amazon
run_financial_analysis("AAPL")