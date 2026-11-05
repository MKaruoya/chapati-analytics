import pandas as pd
import numpy as np

# Read raw with multi-level headers
df_raw = pd.read_csv('data/october_dataset.csv', header=[0, 1, 2])

print("Extracting actual weekly data (corrected interpretation)...\n")

# Month map
month_map = {
    'March': 1, 'April': 2, 'May': 3, 'June': 4,
    'July': 5, 'August': 6, 'September': 7, 'October': 8
}

weekly_records = []

for branch_idx, (_, branch_row) in enumerate(df_raw.iterrows()):
    branch_name = branch_row.iloc[0]
    
    # Skip invalid branches
    if pd.isna(branch_name):
        continue
    branch_name_str = str(branch_name).strip()
    if 'CHAPATI' in branch_name_str.upper() or 'Row Labels' in branch_name_str or 'Column Labels' in branch_name_str:
        continue
    
    col_idx = 1
    week_counter = 1
    
    for month_num in range(1, 9):  # 8 months
        # Find month header
        month_found = False
        while col_idx < len(branch_row):
            col_header = str(df_raw.columns[col_idx])
            
            # Check if this is our month
            month_name = None
            for m_name, m_num in month_map.items():
                if m_name in col_header and 'Sum of' not in col_header:
                    month_name = m_name
                    break
            
            if month_name and month_map[month_name] == month_num:
                month_found = True
                col_idx += 1
                break
            elif 'Sum of' in col_header:
                col_idx += 2
                break
            else:
                col_idx += 1
        
        if not month_found:
            continue
        
        # Read weeks for this month
        # Pattern: Sales (odd), Adjustment (even), Sales (odd), Adjustment (even), ...
        
        while col_idx < len(branch_row):
            col_header = str(df_raw.columns[col_idx])
            
            # Stop at totals or next month
            if 'Sum of' in col_header:
                col_idx += 2
                break
            
            is_new_month = False
            for m_name in month_map.keys():
                if m_name in col_header and month_map[m_name] != month_num:
                    is_new_month = True
                    break
            
            if is_new_month:
                break
            
            # Get Sales value (current column)
            sales_val = branch_row.iloc[col_idx]
            col_idx += 1
            
            # Get Adjustment value (next column)
            adjustment_val = None
            if col_idx < len(branch_row):
                adjustment_val = branch_row.iloc[col_idx]
                col_idx += 1
            
            # Process values
            try:
                sales = float(sales_val) if pd.notna(sales_val) else 0
                adjustment = float(adjustment_val) if pd.notna(adjustment_val) else 0
                
                # Interpretation:
                # - Sales column: actual sales (can be negative if returns exceeded sales)
                # - Adjustment column: negative returns (so abs(adjustment) = returns)
                
                # If sales is negative, it means returns exceeded sales
                # So: actual_sales = max(0, sales)
                #     returns = abs(adjustment) + abs(min(0, sales))
                
                if sales < 0:
                    # Negative sales means returns exceeded sales
                    actual_sales = 0
                    returns = abs(adjustment) + abs(sales)
                else:
                    actual_sales = sales
                    returns = abs(adjustment)
                
                # Only record if at least one value is non-zero
                if actual_sales != 0 or returns != 0:
                    order_qty = actual_sales + returns
                    return_rate = (returns / order_qty * 100) if order_qty > 0 else 0
                    
                    weekly_records.append({
                        'Branch': branch_name,
                        'Month': month_num,
                        'Week': week_counter,
                        'Sales': int(actual_sales),
                        'Returns': int(returns),
                        'Return Rate': round(return_rate, 1)
                    })
                    week_counter += 1
            except:
                pass

print(f"Extracted {len(weekly_records)} weekly records\n")

if weekly_records:
    weekly_df = pd.DataFrame(weekly_records)
    
    print("Sample data:")
    print(weekly_df.head(50))
    
    print("\n\nSample for CASH SALES - SPECIAL-THIKA BRANCH:")
    sample_branch = weekly_df[weekly_df['Branch'] == 'CASH SALES - SPECIAL-THIKA BRANCH']
    if len(sample_branch) > 0:
        print(sample_branch.to_string())
    
    # Verify against monthly totals
    print("\n\nVerification - comparing weekly totals to monthly:")
    for branch in weekly_df['Branch'].unique()[:5]:
        branch_weekly = weekly_df[weekly_df['Branch'] == branch]
        for month in sorted(branch_weekly['Month'].unique()):
            month_data = branch_weekly[branch_weekly['Month'] == month]
            weekly_sales = month_data['Sales'].sum()
            weekly_returns = month_data['Returns'].sum()
            order = weekly_sales + weekly_returns
            return_rate = (weekly_returns / order * 100) if order > 0 else 0
            print(f"{branch} M{int(month)}: Sales={weekly_sales}, Returns={weekly_returns}, Return Rate={return_rate:.1f}%")
          # Save as Excel
    weekly_df.to_excel('data/october_weekly_actual.xlsx', index=False)
    print(f"Saved to october_weekly_actual.xlsx")
    print(f"Total records: {len(weekly_df)}")
else:
    print("No records extracted")
