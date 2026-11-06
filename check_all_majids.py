import pandas as pd

# Read raw with multi-level headers
df_raw = pd.read_csv('data/october_dataset.csv', header=[0, 1, 2])

print("All MAJID branches:\n")

majid_count = 0

# Find all MAJID branches
for idx in range(len(df_raw)):
    branch_name = df_raw.iloc[idx, 0]
    if pd.notna(branch_name) and 'MAJID' in str(branch_name).upper():
        majid_count += 1
        print(f"\n{'='*80}")
        print(f"MAJID #{majid_count}: {branch_name}")
        print(f"{'='*80}")
        
        print("\nColumn | Header | Value")
        print("-" * 80)
        
        for col_idx in range(1, 51):
            col_header = df_raw.columns[col_idx]
            col_value = df_raw.iloc[idx, col_idx]
            
            header_str = str(col_header)[:50]
            print(f"{col_idx:3d} | {header_str:50s} | {col_value}")
        
        if majid_count >= 3:  # Show first 3 MAJID branches
            break

print(f"\n\nTotal MAJID branches found: {majid_count}")
