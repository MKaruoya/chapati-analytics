import pandas as pd

# Read raw with multi-level headers
df_raw = pd.read_csv('data/october_dataset.csv', header=[0, 1, 2])

print("Looking for MAJID branch...\n")

# Find a MAJID branch
for idx in range(len(df_raw)):
    branch_name = df_raw.iloc[idx, 0]
    if pd.notna(branch_name) and 'MAJID' in str(branch_name).upper():
        print(f"Branch: {branch_name}\n")
        
        print("Column | Header | Value")
        print("-" * 80)
        
        for col_idx in range(1, 51):
            col_header = df_raw.columns[col_idx]
            col_value = df_raw.iloc[idx, col_idx]
            
            header_str = str(col_header)[:50]
            print(f"{col_idx:3d} | {header_str:50s} | {col_value}")
        
        break
