import pandas as pd
import numpy as np

# Read the October dataset with multi-level headers
df_oct = pd.read_csv('data/october_dataset.csv', header=[0, 1, 2])

print("Reading October data...")
print(f"Original shape: {df_oct.shape}")

# Get the first column (Branch names)
branch_col = df_oct.iloc[:, 0]

# Extract only columns that contain "Sum of" (actual data columns)
data_cols = []
for i, col in enumerate(df_oct.columns):
    col_str = str(col)
    if 'Sum of' in col_str:
        data_cols.append(i)

print(f"Found {len(data_cols)} data columns")

# Extract branch and data columns
df_clean = df_oct.iloc[:, [0] + data_cols].copy()

# Flatten the multi-index columns
new_columns = ['Branch']
month_map = {
    'March': 1, 'April': 2, 'May': 3, 'June': 4,
    'July': 5, 'August': 6, 'September': 7, 'October': 8
}

for col in df_clean.columns[1:]:
    col_str = str(col)
    
    # Find month
    month_num = None
    for month_name, num in month_map.items():
        if month_name in col_str:
            month_num = num
            break
    
    # Find metric type
    if month_num:
        if 'Returns' in col_str:
            new_columns.append(f'M{month_num}_Returns')
        elif 'Sales' in col_str:
            new_columns.append(f'M{month_num}_Sales')
    else:
        new_columns.append(str(col))

df_clean.columns = new_columns

print(f"Cleaned columns: {df_clean.columns.tolist()}")

# Filter: Keep only rows that contain branch identifiers
df_clean['Branch'] = df_clean['Branch'].astype(str)
df_clean = df_clean[~df_clean['Branch'].str.contains('CHAPATI|SOKO|Row Labels|Unnamed|Column Labels', case=False, na=False)]

# Remove rows with no branch name
df_clean = df_clean[df_clean['Branch'].notna()]
df_clean = df_clean[df_clean['Branch'] != '']
df_clean = df_clean[df_clean['Branch'].str.strip() != '']

# Fill NaN with 0
df_clean = df_clean.fillna(0)

# Reset index
df_clean = df_clean.reset_index(drop=True)
# Remove the Total columns (last 2 columns)
df_clean = df_clean.iloc[:, :-2]

# Save
df_clean.to_csv('data/october_dataset_transformed.csv', index=False)

print("✅ October data transformed successfully!")
print(f"Branches: {len(df_clean)}")
print(f"Columns: {len(df_clean.columns)}")
print(f"\nFinal columns: {df_clean.columns.tolist()}")
print("\nFirst few rows:")
print(df_clean.head())
print("\nData types:")
print(df_clean.dtypes)
