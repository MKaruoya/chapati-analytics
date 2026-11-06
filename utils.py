import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def extract_outlet_name(branch_name):
    """Extract outlet name from branch name"""
    if pd.isna(branch_name):
        return "Unknown"
    
    branch_str = str(branch_name).strip()
    
    # Remove common prefixes
    prefixes = ['CASH CUSTOMER', 'CASH SALES', 'CASH SALES STAFF']
    for prefix in prefixes:
        if branch_str.startswith(prefix):
            branch_str = branch_str.replace(prefix, '').strip()
            branch_str = branch_str.lstrip('-').strip()
            break
    
    return branch_str if branch_str else "Unknown"

def calculate_monthly_metrics(branch_row, numeric_cols):
    """Calculate monthly metrics from branch data"""
    metrics = []
    
    # Handle both Series and DataFrame
    if isinstance(branch_row, pd.DataFrame):
        branch_row = branch_row.iloc[0]
    
    month_map = {
        'M1': 1, 'M2': 2, 'M3': 3, 'M4': 4,
        'M5': 5, 'M6': 6, 'M7': 7, 'M8': 8
    }
    
    for month_label, month_num in month_map.items():
        sales_col = f'{month_label}_Sales'
        returns_col = f'{month_label}_Returns'
        
        if sales_col in branch_row.index and returns_col in branch_row.index:
            sales = float(branch_row[sales_col]) if sales_col in branch_row.index else 0
            returns = float(branch_row[returns_col]) if returns_col in branch_row.index else 0
            
            if sales > 0 or returns > 0:
                order_qty = sales + returns
                return_rate = (returns / order_qty * 100) if order_qty > 0 else 0
                
                metrics.append({
                    'month_num': month_num,
                    'sales': sales,
                    'returns': returns,
                    'return_rate': return_rate,
                    'has_data': True
                })
            else:
                metrics.append({
                    'month_num': month_num,
                    'sales': 0,
                    'returns': 0,
                    'return_rate': 0,
                    'has_data': False
                })
    
    return metrics

def get_month_from_week(week_num):
    """Convert ISO week number (2026) to month number (1-8 for March-October)"""
    
    week_to_month = {
        10: 1, 11: 1, 12: 1, 13: 1, 14: 1,      # March = M1
        15: 2, 16: 2, 17: 2, 18: 2,              # April = M2
        19: 3, 20: 3, 21: 3, 22: 3,              # May = M3
        23: 4, 24: 4, 25: 4, 26: 4, 27: 4,      # June = M4
        28: 5, 29: 5, 30: 5, 31: 5,              # July = M5
        32: 6, 33: 6, 34: 6, 35: 6, 36: 6,      # August = M6
        37: 7, 38: 7, 39: 7, 40: 7,              # September = M7
        41: 8, 42: 8, 43: 8, 44: 8,              # October = M8
    }
    
    return week_to_month.get(week_num, None)

def add_month_to_weekly_data(df):
    """Add month column to weekly data based on week number"""
    if 'Week' not in df.columns:
        return df
    
    df = df.copy()
    df['Month'] = df['Week'].apply(get_month_from_week)
    
    # Calculate return rate if not present
    if 'Return Rate' not in df.columns:
        df['Return Rate'] = 0.0
        for idx, row in df.iterrows():
            if pd.notna(row.get('Sales')) and pd.notna(row.get('Returns')):
                sales = float(row['Sales'])
                returns = float(row['Returns'])
                order_qty = sales + returns
                if order_qty > 0:
                    df.at[idx, 'Return Rate'] = round((returns / order_qty * 100), 1)
    
    return df

def get_store_weekly_data(weekly_df, branch_name):
    """Get weekly data for a specific store"""
    if weekly_df is None or len(weekly_df) == 0:
        return None
    
    store_data = weekly_df[weekly_df['Branch'] == branch_name].copy()
    
    if len(store_data) == 0:
        return None
    
    # Ensure Month column exists
    if 'Month' not in store_data.columns:
        store_data = add_month_to_weekly_data(store_data)
    
    return store_data.sort_values('Week').reset_index(drop=True)

def get_monthly_summary_from_weekly(weekly_df, branch_name):
    """Calculate monthly summary from weekly data"""
    store_weekly = get_store_weekly_data(weekly_df, branch_name)
    
    if store_weekly is None or len(store_weekly) == 0:
        return None
    
    monthly_summary = []
    
    for month in sorted(store_weekly['Month'].unique()):
        month_data = store_weekly[store_weekly['Month'] == month]
        
        sales = month_data['Sales'].sum()
        returns = month_data['Returns'].sum()
        order_qty = sales + returns
        return_rate = (returns / order_qty * 100) if order_qty > 0 else 0
        
        monthly_summary.append({
            'month_num': month,
            'sales': sales,
            'returns': returns,
            'return_rate': return_rate,
            'has_data': True
        })
    
    return pd.DataFrame(monthly_summary)

def calculate_volatility(values):
    """Calculate volatility (standard deviation) of values"""
    if len(values) < 2:
        return 0
    return np.std(values)

def get_sales_volume_category(sales):
    """Categorize sales volume"""
    if sales > 500:
        return "High Volume"
    elif sales > 200:
        return "Medium Volume"
    else:
        return "Low Volume"

def calculate_quarter_trend(monthly_df):
    """Calculate trend for each quarter"""
    if len(monthly_df) < 3:
        return "Insufficient Data"
    
    # Get last 3 months
    recent = monthly_df.tail(3)['return_rate'].values
    
    if recent[-1] < recent[0] - 2:
        return "Declining"
    elif recent[-1] > recent[0] + 2:
        return "Rising"
    else:
        return "Stable"

def get_active_periods(branch_row, numeric_cols):
    """Get months with active data"""
    # Handle both Series and DataFrame
    if isinstance(branch_row, pd.DataFrame):
        branch_row = branch_row.iloc[0]
    
    active_months = []
    
    month_map = {
        'M1': 1, 'M2': 2, 'M3': 3, 'M4': 4,
        'M5': 5, 'M6': 6, 'M7': 7, 'M8': 8
    }
    
    for month_label, month_num in month_map.items():
        sales_col = f'{month_label}_Sales'
        returns_col = f'{month_label}_Returns'
        
        if sales_col in branch_row.index and returns_col in branch_row.index:
            sales = float(branch_row[sales_col])
            returns = float(branch_row[returns_col])
            
            if sales > 0 or returns > 0:
                active_months.append(month_num)
    
    return active_months

def get_top_performers(df, metric='return_rate', n=5):
    """Get top performing branches"""
    metrics_list = []
    
    for _, branch_row in df.iterrows():
        branch_name = branch_row['Branch']
        numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
        monthly_data = calculate_monthly_metrics(branch_row, numeric_cols)
        monthly_df = pd.DataFrame(monthly_data)
        monthly_df = monthly_df[monthly_df['has_data'] == True]
        
        if len(monthly_df) > 0:
            if metric == 'return_rate':
                score = monthly_df['return_rate'].mean()
            else:
                score = monthly_df['sales'].sum()
            
            metrics_list.append({
                'branch': branch_name,
                'score': score,
                'avg_return_rate': monthly_df['return_rate'].mean(),
                'total_sales': monthly_df['sales'].sum()
            })
    
    metrics_df = pd.DataFrame(metrics_list)
    
    if metric == 'return_rate':
        # Lower return rate is better
        return metrics_df.nsmallest(n, 'score')
    else:
        # Higher sales is better
        return metrics_df.nlargest(n, 'score')

def get_bottom_performers(df, metric='return_rate', n=5):
    """Get bottom performing branches"""
    metrics_list = []
    
    for _, branch_row in df.iterrows():
        branch_name = branch_row['Branch']
        numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
        monthly_data = calculate_monthly_metrics(branch_row, numeric_cols)
        monthly_df = pd.DataFrame(monthly_data)
        monthly_df = monthly_df[monthly_df['has_data'] == True]
        
        if len(monthly_df) > 0:
            if metric == 'return_rate':
                score = monthly_df['return_rate'].mean()
            else:
                score = monthly_df['sales'].sum()
            
            metrics_list.append({
                'branch': branch_name,
                'score': score,
                'avg_return_rate': monthly_df['return_rate'].mean(),
                'total_sales': monthly_df['sales'].sum()
            })
    
    metrics_df = pd.DataFrame(metrics_list)
    
    if metric == 'return_rate':
        # Higher return rate is worse
        return metrics_df.nlargest(n, 'score')
    else:
        # Lower sales is worse
        return metrics_df.nsmallest(n, 'score')
