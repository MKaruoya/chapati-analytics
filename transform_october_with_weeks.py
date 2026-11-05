import pandas as pd
import numpy as np

# Read raw with multi-level headers
df_raw = pd.read_csv('data/october_dataset.csv', header=[0, 1, 2])

print("Reading October data with weekly breakdown...")
print(f"Original shape: {df_raw.shape}")

# Get branch column
branch_col = df_raw.iloc[:, 0]

# Extract monthly totals (Sum of Bales Returns and Sum of Net Bales Sales)
month_map = {
    'March': 1, 'April': 2, 'May': 3, 'June': 4,
    'July': 5, 'August': 6, 'September': 7, 'October': 8
}

# Find columns with "Sum of"
monthly_cols = []
for i, col in enumerate(df_raw.columns):
    col_str = str(col)
    if 'Sum of' in col_str:
        monthly_cols.append(i)

print(f"Found {len(monthly_cols)} monthly total columns")

# Extract branch and monthly data
df_monthly = df_raw.iloc[:, [0] + monthly_cols].copy()

# Flatten column names for monthly data
new_columns = ['Branch']
for col in df_monthly.columns[1:]:
    col_str = str(col)
    
    month_num = None
    for month_name, num in month_map.items():
        if month_name in col_str:
            month_num = num
            break
    
    if month_num:
        if 'Returns' in col_str:
            new_columns.append(f'M{month_num}_Returns')
        elif 'Sales' in col_str:
            new_columns.append(f'M{month_num}_Sales')
    else:
        new_columns.append(f'Other_{len(new_columns)}')

# Ensure length matches
if len(new_columns) != len(df_monthly.columns):
    new_columns = new_columns[:len(df_monthly.columns)]

df_monthly.columns = new_columns

# Remove Total columns (last 2)
cols_to_keep = [c for c in df_monthly.columns if not c.startswith('Other_')]
df_monthly = df_monthly[cols_to_keep]

# Clean branches
df_monthly['Branch'] = df_monthly['Branch'].astype(str)
df_monthly = df_monthly[~df_monthly['Branch'].str.contains(
    'CHAPATI|SOKO|Row Labels|Unnamed|Column Labels', 
    case=False, 
    na=False
)]

df_monthly = df_monthly[df_monthly['Branch'].notna()]
df_monthly = df_monthly[df_monthly['Branch'] != '']
df_monthly = df_monthly[df_monthly['Branch'].str.strip() != '']

df_monthly = df_monthly.fillna(0)
df_monthly = df_monthly.reset_index(drop=True)

# Save monthly version
df_monthly.to_csv('data/october_dataset_transformed.csv', index=False)
print(f"Saved monthly data: {df_monthly.shape}")
print(f"Monthly columns: {df_monthly.columns.tolist()}")

print("\nTransformation complete!")
