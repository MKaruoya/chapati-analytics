import pandas as pd
import numpy as np

# Read the October dataset with multi-level headers
df_oct = pd.read_csv('data/october_dataset.csv', header=[0, 1, 2])

# Flatten multi-level columns
new_columns = []
for col in df_oct.columns:
    if 'March' in str(col):
        metric = 'Returns' if 'Returns' in str(col) else 'Sales'
        new_columns.append(f'M1_{metric}')
    elif 'April' in str(col):
        metric = 'Returns' if 'Returns' in str(col) else 'Sales'
        new_columns.append(f'M2_{metric}')
    elif 'May' in str(col):
        metric = 'Returns' if 'Returns' in str(col) else 'Sales'
        new_columns.append(f'M3_{metric}')
    elif 'June' in str(col):
        metric = 'Returns' if 'Returns' in str(col) else 'Sales'
        new_columns.append(f'M4_{metric}')
    elif 'July' in str(col):
        metric = 'Returns' if 'Returns' in str(col) else 'Sales'
        new_columns.append(f'M5_{metric}')
    elif 'August' in str(col):
        metric = 'Returns' if 'Returns' in str(col) else 'Sales'
        new_columns.append(f'M6_{metric}')
    elif 'September' in str(col):
        metric = 'Returns' if 'Returns' in str(col) else 'Sales'
        new_columns.append(f'M7_{metric}')
    elif 'October' in str(col):
        metric = 'Returns' if 'Returns' in str(col) else 'Sales'
        new_columns.append(f'M8_{metric}')
    else:
        new_columns.append(str(col))

df_oct.columns = new_columns

# Get the first column as Branch
df_oct = df_oct.iloc[:, :17]  # Keep only M1-M8 (16 columns) + Branch

# Rename first column to Branch
first_col = df_oct.columns[0]
df_oct.rename(columns={first_col: 'Branch'}, inplace=True)

# Filter: Keep only rows that contain branch identifiers (have '-' or are customer segments)
# Remove product rows (they contain "CHAPATI", "SOKO", etc.)
df_oct['Branch'] = df_oct['Branch'].astype(str)
df_oct = df_oct[~df_oct['Branch'].str.contains('CHAPATI|SOKO|Row Labels', case=False, na=False)]

# Remove rows with no branch name
df_oct = df_oct[df_oct['Branch'].notna()]
df_oct = df_oct[df_oct['Branch'] != '']
df_oct = df_oct[df_oct['Branch'].str.strip() != '']

# Fill NaN with 0
df_oct = df_oct.fillna(0)

# Reset index
df_oct = df_oct.reset_index(drop=True)

# Save
df_oct.to_csv('data/october_dataset_transformed.csv', index=False)

print("✅ October data transformed successfully!")
print(f"Branches: {len(df_oct)}")
print(f"Columns: {len(df_oct.columns)}")
print("\nFirst few rows:")
print(df_oct.head(10))
