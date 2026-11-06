import pandas as pd
import numpy as np

# Read raw with multi-level headers
df_raw = pd.read_csv('data/october_dataset.csv', header=[0, 1, 2])

print("Extracting weekly data (skipping separator columns)...\n")

# Get branch column
branch_col = df_raw.iloc[:, 0]

# Month map
month_map = {
    'March': 1, 'April': 2, 'May': 3, 'June': 4,
    'July': 5, 'August': 6, 'September': 7, 'October': 8
}

# Find actual data columns (skip blanks/separators)
data_cols = []
for i, col in enumerate(df_raw.columns):
    col_str = str(col)
    # Data columns have either a month name OR a week number (10-44)
    if 'Sum of' not in col_str:
        has_month = any(month in col_str for month in month_map.keys())
        has_week = any(str(w) in col_str for w in range(10, 45))
        
        if has_month or has_week:
            data_cols.append(i)

print(f"Found {len(data_cols)} data columns (excluding separators)\n")

# Extract branch and data
df_data = df_raw.iloc[:, [0] + data_cols].copy()

# Now parse the structure
# Each month section has: Month header, then 4-5 weeks of data
weekly_records = []

for branch_idx, (_, branch_row) in enumerate(df_data.iterrows()):
    branch_name = branch_row.iloc[0]
    
    # Skip invalid branches
    if pd.isna(branch_name):
        continue
    branch_name_str = str(branch_name).strip()
    if 'CHAPATI' in branch_name_str.upper() or 'Row Labels' in branch_name_str or 'Column Labels' in branch_name_str:
        continue
    
    # Parse the data columns
    col_idx = 1
    
    for month_num in range(1, 9):  # 8 months
        # Skip month header column if present
        if col_idx < len(branch_row):
            col_val = str(branch_row.iloc[col_idx])
            # Check if this is a month header
            month_found = False
            for month_name in month_map.keys():
                if month_name in col_val:
                    month_found = True
                    col_idx += 1
                    break
        
        # Now read the weeks for this month
        # We don't know exactly how many, so read until we hit the next month or end
        week_in_month = 1
        
        while col_idx < len(branch_row):
            col_val = branch_row.iloc[col_idx]
            col_str = str(col_val)
            
            # Check if this is a new month header
            is_new_month = False
            for month_name in month_map.keys():
                if month_name in str(branch_row.index[col_idx] if hasattr(branch_row, 'index') else ''):
                    is_new_month = True
                    break
            
            if is_new_month:
                break
            
            # Try to parse as a number
            try:
                value = float(col_val)
                weekly_records.append({
                    'Branch': branch_name,
                    'Month': month_num,
                    'Week': week_in_month,
                    'Value': value
                })
                week_in_month += 1
            except:
                # Not a number, might be a separator or month header
                pass
            
            col_idx += 1

print(f"Extracted {len(weekly_records)} weekly records\n")

if weekly_records:
    weekly_df = pd.DataFrame(weekly_records)
    print("Sample data:")
    print(weekly_df.head(30))
    print("\n...")
    print(weekly_df.tail(10))
    
    # Save
    weekly_df.to_csv('data/october_weekly_raw.csv', index=False)
    print(f"\nSaved to october_weekly_raw.csv")
else:
    print("No weekly records extracted!")
