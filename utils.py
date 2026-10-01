import numpy as np

def calculate_volatility(monthly_data):
    return_rates = [m['return_rate'] for m in monthly_data if m['has_data']]
    return np.std(return_rates) if len(return_rates) > 1 else 0

def get_sales_volume_category(total_sales):
    abs_sales = abs(total_sales)
    if abs_sales > 500: return "High Volume"
    elif abs_sales > 200: return "Medium Volume"
    elif abs_sales > 50: return "Low Volume"
    else: return "Very Low Volume"

def extract_outlet_name(branch_name):
    if isinstance(branch_name, str) and '-' in branch_name:
        return branch_name.split('-')[0].strip()
    return None

def calculate_quarter_trend(monthly_data):
    active_months = [m for m in monthly_data if m['has_data']]
    if len(active_months) < 3:
        return None, None, None
    last_quarter = active_months[-3:]
    last_quarter_avg = np.mean([m['return_rate'] for m in last_quarter])
    if len(active_months) >= 6:
        prev_quarter = active_months[-6:-3]
        prev_quarter_avg = np.mean([m['return_rate'] for m in prev_quarter])
        quarter_change = last_quarter_avg - prev_quarter_avg
        trend = "Improving" if quarter_change < -2 else "Worsening" if quarter_change > 2 else "Stable"
    else:
        quarter_change = None
        trend = "N/A"
    return last_quarter_avg, quarter_change, trend

def calculate_weekly_metrics(branch_row, numeric_cols):
    weekly_data = []
    for i in range(0, len(numeric_cols) - 1, 2):
        net_sales_val = pd.to_numeric(branch_row[numeric_cols[i]].values[0], errors='coerce')
        returns_val = pd.to_numeric(branch_row[numeric_cols[i + 1]].values[0], errors='coerce')
        if pd.notna(net_sales_val) or pd.notna(returns_val):
            net_sales_val = net_sales_val if pd.notna(net_sales_val) else 0
            returns_val = returns_val if pd.notna(returns_val) else 0
            original_order = abs(net_sales_val) + returns_val
            return_pct = (returns_val / original_order * 100) if original_order > 0 else 0
            weekly_data.append({'week': len(weekly_data) + 1, 'order_quantity': original_order, 'net_sales': net_sales_val, 'returns': returns_val, 'return_pct': return_pct})
    return weekly_data

def find_optimal_quantity(weekly_data):
    active_weeks = [w for w in weekly_data if w['order_quantity'] > 0]
    if not active_weeks:
        return None, None, None, "No data", 0
    quantities = [w['order_quantity'] for w in active_weeks]
    returns = [w['return_pct'] for w in active_weeks]
    q1 = np.percentile(quantities, 25)
    q3 = np.percentile(quantities, 75)
    q1_returns = [r for q, r in zip(quantities, returns) if q <= q1]
    q2_returns = [r for q, r in zip(quantities, returns) if q1 < q <= q3]
    q3_returns = [r for q, r in zip(quantities, returns) if q > q3]
    avg_q1_return = np.mean(q1_returns) if q1_returns else 0
    avg_q2_return = np.mean(q2_returns) if q2_returns else 0
    avg_q3_return = np.mean(q3_returns) if q3_returns else 0
    quartile_returns = {'Q1': (q1, avg_q1_return), 'Q2': (np.percentile(quantities, 50), avg_q2_return), 'Q3': (q3, avg_q3_return)}
    best_quartile = min(quartile_returns.items(), key=lambda x: x[1][1])
    optimal_qty = best_quartile[1][0]
    optimal_return_rate = best_quartile[1][1]
    corr = np.corrcoef(quantities, returns)[0, 1]
    confidence = min(len(active_weeks) / 35, 1.0)
    return optimal_qty, optimal_return_rate, corr, best_quartile[0], confidence

import pandas as pd
