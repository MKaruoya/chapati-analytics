import pandas as pd
import numpy as np

print("Transforming October Dataset 1 to weekly format...\n")

# Read the raw CSV
df_raw = pd.read_csv('data/October dataset 1.csv', header=None)

print(f"Raw shape: {df_raw.shape}")
print(f"\nFirst 4 rows (first 12 columns):")
print(df_raw.iloc[:4, :12])

# Row 1 has week numbers (0-indexed)
weeks_row = df_raw.iloc[1, 1:].values

# Row 2 has metrics
metrics_row = df_raw.iloc[2, 1:].values

print(f"\nWeeks row (first 12): {weeks_row[:12]}")
print(f"Metrics row (first 12): {metrics_row[:12]}")

# Extract weeks and their column positions
weeks_dict = {}  # week -> {'returns': col, 'sales': col}

current_week = None
for col_idx in range(len(weeks_row)):
    week = weeks_row[col_idx]
    metric = metrics_row[col_idx]
    
    # Track current week
    if pd.notna(week):
        try:
            current_week = int(float(week))
            if current_week not in weeks_dict:
                weeks_dict[current_week] = {'returns': None, 'sales': None}
        except:
            pass
    
    # Assign metric to current week
    if current_week is not None and pd.notna(metric):
        if 'Returns' in str(metric):
            weeks_dict[current_week]['returns'] = col_idx + 1
        elif 'Sales' in str(metric):
            weeks_dict[current_week]['sales'] = col_idx + 1

weeks = sorted(weeks_dict.keys())
print(f"\nWeeks found: {weeks}")
print(f"Week structure: {weeks_dict}")

# Data starts from row 3
data_rows = df_raw.iloc[3:, :]

# Extract branches (first column)
branches_col = data_rows.iloc[:, 0].values

print(f"\nProcessing {len(branches_col)} rows...")

# Transform to weekly format
weekly_records = []

for row_idx, branch in enumerate(branches_col):
    if pd.isna(branch):
        continue
    
    branch_str = str(branch).strip()
    
    # Skip product rows - keep only branch rows (contain '-' and not product names)
    if '-' not in branch_str:
        continue
    
    if 'CHAPATI' in branch_str.upper() or 'SOKO' in branch_str.upper():
        continue
    
    # This is a branch row
    for week, cols in weeks_dict.items():
        sales_val = 0
        returns_val = 0
        
        # Get sales value
        if cols['sales'] is not None:
            try:
                val = data_rows.iloc[row_idx, cols['sales']]
                if pd.notna(val):
                    sales_val = float(val)
            except:
                pass
        
        # Get returns value
        if cols['returns'] is not None:
            try:
                val = data_rows.iloc[row_idx, cols['returns']]
                if pd.notna(val):
                    returns_val = float(val)
            except:
                pass
        
        if sales_val > 0 or returns_val > 0:
            weekly_records.append({
                'Branch': branch_str,
                'Week': week,
                'Sales': int(sales_val),
                'Returns': int(returns_val)
            })

if len(weekly_records) > 0:
    weekly_df = pd.DataFrame(weekly_records)
    
    print(f"\n✅ Transformed to {len(weekly_df)} weekly records")
    print(f"Branches: {weekly_df['Branch'].nunique()}")
    print(f"Weeks: {sorted(weekly_df['Week'].unique())}")
    
    print(f"\nSample data:")
    print(weekly_df.head(30))
    
    # Save
    weekly_df.to_csv('data/october_weekly_actual.csv', index=False)
    print(f"\n✅ Saved to october_weekly_actual.csv")
else:
    print("\n❌ No records extracted!")
