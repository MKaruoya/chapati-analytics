import pandas as pd
import numpy as np

# Read raw with multi-level headers
df_raw = pd.read_csv('data/october_dataset.csv', header=[0, 1, 2])

print("Extracting actual weekly data (Sales and Returns separated)...\n")

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
            
            # Get Returns/Adjustment value (next column)
            returns_val = None
            if col_idx < len(branch_row):
                returns_val = branch_row.iloc[col_idx]
                col_idx += 1
            
            # Process values
            try:
                sales = float(sales_val) if pd.notna(sales_val) else 0
                returns = float(returns_val) if pd.notna(returns_val) else 0
                
                # Only record if at least one value is non-zero
                if sales != 0 or returns != 0:
                    # Returns should be positive, so if negative, it's an adjustment
                    if returns < 0:
                        returns = abs(returns)
                    
                    weekly_records.append({
                        'Branch': branch_name,
                        'Month': month_num,
                        'Week': week_counter,
                        'Sales': int(sales),
                        'Returns': int(returns)
                    })
                    week_counter += 1
            except:
                pass

print(f"Extracted {len(weekly_records)} weekly records\n")

if weekly_records:
    weekly_df = pd.DataFrame(weekly_records)
    
    # Calculate return rate
    weekly_df['Return Rate'] = (weekly_df['Returns'] / (weekly_df['Sales'] + weekly_df['Returns']) * 100).round(1)
    weekly_df.loc[weekly_df['Sales'] + weekly_df['Returns'] == 0, 'Return Rate'] = 0
    
    print("Sample data:")
    print(weekly_df.head(50))
    
    print("\n\nSample for one branch (first 20 weeks):")
    sample_branch = weekly_df[weekly_df['Branch'] == weekly_df.iloc[0]['Branch']].head(20)
    print(sample_branch)
    
    # Save
    weekly_df.to_csv('data/october_weekly_actual.csv', index=False)
    print(f"\nSaved to october_weekly_actual.csv")
    print(f"Total records: {len(weekly_df)}")
else:
    print("No records extracted")
