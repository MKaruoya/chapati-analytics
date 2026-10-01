import pandas as pd
import numpy as np

def get_active_periods(monthly_data):
    """Identify active periods (continuous months with data) and gaps"""
    if not monthly_data:
        return []
    
    periods = []
    current_period = []
    
    for month in monthly_data:
        if month['sales'] != 0 or month['returns'] != 0:
            current_period.append(month)
        else:
            if current_period:
                periods.append(current_period)
                current_period = []
    
    if current_period:
        periods.append(current_period)
    
    return periods

def calculate_monthly_metrics(branch_row, numeric_cols):
    """Calculate metrics for each month"""
    weeks_per_month = 5
    monthly_metrics = []
    
    for month_num in range(1, 10):
        start_idx = (month_num - 1) * weeks_per_month * 2
        end_idx = month_num * weeks_per_month * 2
        
        month_sales = 0
        month_returns = 0
        
        for i in range(start_idx, min(end_idx, len(numeric_cols) - 1), 2):
            if i < len(numeric_cols) - 1:
                try:
                    net_sales_val = pd.to_numeric(branch_row[numeric_cols[i]].values[0], errors='coerce')
                    returns_val = pd.to_numeric(branch_row[numeric_cols[i + 1]].values[0], errors='coerce')
                    
                    if pd.notna(net_sales_val):
                        month_sales += net_sales_val
                    if pd.notna(returns_val):
                        month_returns += returns_val
                except:
                    pass
        
        original_order = abs(month_sales) + month_returns
        if original_order > 0:
            return_rate = (month_returns / original_order) * 100
        else:
            return_rate = 0
        
        monthly_metrics.append({
            'month_num': month_num,
            'month': f"M{month_num}",
            'sales': month_sales,
            'returns': month_returns,
            'return_rate': return_rate,
            'has_data': (month_sales != 0 or month_returns != 0)
        })
    
    return monthly_metrics
