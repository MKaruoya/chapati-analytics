import pandas as pd

# Read raw with multi-level headers
df_raw = pd.read_csv('data/october_dataset.csv', header=[0, 1, 2])

print("Raw data sample (first branch, first 30 columns):\n")

# Get first data branch (skip header rows)
for idx in range(len(df_raw)):
    branch_name = df_raw.iloc[idx, 0]
    if pd.notna(branch_name) and 'CHAPATI' not in str(branch_name).upper() and 'Row' not in str(branch_name):
        print(f"Branch: {branch_name}\n")
        
        print("Column | Header | Value")
        print("-" * 60)
        
        for col_idx in range(1, 31):
            col_header = df_raw.columns[col_idx]
            col_value = df_raw.iloc[idx, col_idx]
            
            print(f"{col_idx:3d} | {str(col_header)[:40]:40s} | {col_value}")
        
        break
