import pandas as pd
import numpy as np

print("Transforming October Dataset 2 - CORRECT extraction\n")

# Read raw
df_raw = pd.read_csv('data/October dataset 2.csv', header=None)

print(f"Raw shape: {df_raw.shape}")

# Extract week numbers from Row 1
week_numbers = []
for col in range(len(df_raw.columns)):
    val = df_raw.iloc[1, col]
    if pd.notna(val):
        val_str = str(val).strip()
        # Extract just the number (e.g., "10" from "10 Sum of Gross Bales Sales")
        try:
            week_num = int(val_str.split()[0])
            if week_num not in week_numbers:
                week_numbers.append((week_num, col))
        except:
            pass

week_numbers = sorted(set(week_numbers))
print(f"Weeks found: {[w[0] for w in week_numbers]}\n")

# Extract data
weekly_records = []

for row_idx in range(4, len(df_raw)):  # Start from row 4 (after headers)
    branch_name = df_raw.iloc[row_idx, 0]
    
    if pd.isna(branch_name):
        continue
    
    branch_str = str(branch_name).strip()
    
    # Skip headers and SKU rows
    if 'Row Labels' in branch_str or 'CHAPATI' in branch_str.upper() or 'SOKO' in branch_str.upper():
        continue
    
    # This is a branch row
    for week_num, col_idx in week_numbers:
        # For each week, get Gross (col_idx), Returns (col_idx+1), Net (col_idx+2)
        try:
            gross = float(df_raw.iloc[row_idx, col_idx])
            returns = float(df_raw.iloc[row_idx, col_idx + 1])
            net = float(df_raw.iloc[row_idx, col_idx + 2])
            
            if pd.isna(gross) or pd.isna(returns):
                continue
            
            if gross > 0 or returns > 0:
                return_rate = (returns / gross * 100) if gross > 0 else 0
                
                weekly_records.append({
                    'Branch': branch_str,
                    'Week': week_num,
                    'Gross Sales': int(gross),
                    'Returns': int(returns),
                    'Net Sales': int(net),
                    'Return Rate': round(return_rate, 1)
                })
        except:
            continue

if len(weekly_records) > 0:
    weekly_df = pd.DataFrame(weekly_records)
    
    print(f"✅ Extracted {len(weekly_df)} records")
    print(f"Branches: {weekly_df['Branch'].nunique()}")
    print(f"Weeks: {sorted(weekly_df['Week'].unique())}")
    
    print(f"\nSample data:")
    print(weekly_df.head(30))
    
    # Check October coverage
    october_weeks = [41, 42, 43, 44]
    october_data = weekly_df[weekly_df['Week'].isin(october_weeks)]
    print(f"\n\nOctober data:")
    print(f"Total October records: {len(october_data)}")
    print(f"Branches with October data: {october_data['Branch'].nunique()}")
    
    # Check CHANDARANA ABC
    chandarana_abc = october_data[october_data['Branch'].str.contains('ABC', na=False)]
    print(f"\nCHANDARANA ABC October records:")
    print(chandarana_abc)
    
    # Save
    weekly_df.to_csv('data/october_weekly_correct.csv', index=False)
    print(f"\n✅ Saved to october_weekly_correct.csv")
else:
    print("❌ No records extracted!")
