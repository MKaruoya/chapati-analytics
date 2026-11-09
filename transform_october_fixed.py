import pandas as pd
import numpy as np

print("Transforming October Dataset 2 - FIXED\n")

# Read raw
df_raw = pd.read_csv('data/October dataset 2.csv', header=None)

print(f"Raw shape: {df_raw.shape}")

# Extract UNIQUE week positions (only first occurrence of each week)
week_positions = {}

for col in range(len(df_raw.columns)):
    val = df_raw.iloc[1, col]
    
    if pd.notna(val):
        val_str = str(val).strip()
        
        # Check if this is a metric column (contains "Sum of")
        if "Sum of Gross" in val_str:
            try:
                week_num = int(val_str.split()[0])
                if week_num not in week_positions:
                    week_positions[week_num] = col
            except:
                pass

week_positions = sorted(week_positions.items())

print(f"Weeks found: {[w[0] for w in week_positions]}\n")

# Extract data
weekly_records = []
skipped_records = []

for row_idx in range(4, len(df_raw)):  # Start from row 4 (after headers)
    branch_name = df_raw.iloc[row_idx, 0]
    
    if pd.isna(branch_name):
        continue
    
    branch_str = str(branch_name).strip()
    
    # Skip headers and SKU rows
    if 'Row Labels' in branch_str or 'CHAPATI' in branch_str.upper() or 'SOKO' in branch_str.upper():
        continue
    
    # This is a branch row
    for week_num, col_idx in week_positions:
        # For each week, get Gross (col_idx), Returns (col_idx+1), Net (col_idx+2)
        try:
            gross_val = df_raw.iloc[row_idx, col_idx]
            returns_val = df_raw.iloc[row_idx, col_idx + 1]
            net_val = df_raw.iloc[row_idx, col_idx + 2]
            
            # Convert to float, handle NaN
            gross = float(gross_val) if pd.notna(gross_val) else 0
            returns = float(returns_val) if pd.notna(returns_val) else 0
            net = float(net_val) if pd.notna(net_val) else 0
            
            # Skip only if BOTH gross and returns are 0
            if gross == 0 and returns == 0:
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
        except Exception as e:
            skipped_records.append({
                'Branch': branch_str,
                'Week': week_num,
                'Error': str(e)
            })
            continue

if len(weekly_records) > 0:
    weekly_df = pd.DataFrame(weekly_records)
    
    print(f"✅ Extracted {len(weekly_df)} records")
    print(f"Branches: {weekly_df['Branch'].nunique()}")
    print(f"Weeks: {sorted(weekly_df['Week'].unique())}")
    
    print(f"\nSkipped records: {len(skipped_records)}")
    
    # Check October coverage
    october_weeks = [41, 42, 43, 44]
    october_data = weekly_df[weekly_df['Week'].isin(october_weeks)]
    print(f"\n\nOctober data:")
    print(f"Total October records: {len(october_data)}")
    print(f"Branches with October data: {october_data['Branch'].nunique()}")
    
    # Check ADLIFE
    adlife = october_data[october_data['Branch'].str.contains('ADLIFE', na=False)]
    print(f"\nADLIFE October records:")
    print(adlife)
    
    # Save
    weekly_df.to_csv('data/october_weekly_correct_fixed.csv', index=False)
    print(f"\n✅ Saved to october_weekly_correct_fixed.csv")
    
    # Compare old vs new
    print(f"\n\nComparison:")
    df_old = pd.read_csv('data/october_weekly_correct.csv')
    print(f"Old file October records: {len(df_old[df_old['Week'].isin(october_weeks)])}")
    print(f"New file October records: {len(october_data)}")
    print(f"Difference: {len(october_data) - len(df_old[df_old['Week'].isin(october_weeks)])} new records")

else:
    print("❌ No records extracted!")
