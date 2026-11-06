import pandas as pd
import numpy as np

print("Transforming October Dataset 2 (with SKU breakdown)...\n")

# Read the file with multi-level headers
df = pd.read_csv('data/October dataset 2.csv', header=[0, 1, 2])

print(f"Original shape: {df.shape}")

# Extract week numbers from level 1
weeks = []
for col in df.columns:
    if isinstance(col, tuple) and len(col) >= 2:
        week_str = col[1]
        try:
            week_num = int(week_str.split()[0])
            if week_num not in weeks:
                weeks.append(week_num)
        except:
            pass

weeks = sorted(set(weeks))
print(f"Weeks found: {weeks}\n")

# Extract data with SKU breakdown
weekly_records = []
current_branch = None

for idx, row in df.iterrows():
    # Get first column (Branch or SKU name)
    name = row.iloc[0] if len(row) > 0 else None
    
    if pd.isna(name):
        continue
    
    name_str = str(name).strip()
    
    # Skip headers
    if 'Row Labels' in name_str or 'Column Labels' in name_str:
        continue
    
    # Check if this is a branch row (contains '-' and not a product name)
    is_branch = '-' in name_str and 'CHAPATI' not in name_str.upper() and 'SOKO' not in name_str.upper()
    
    if is_branch:
        current_branch = name_str
        continue
    
    # This is a SKU row
    if current_branch is None:
        continue
    
    sku_name = name_str
    
    for week in weeks:
        # Find columns for this week
        gross_val = None
        returns_val = None
        net_val = None
        
        for col in df.columns:
            if isinstance(col, tuple) and len(col) >= 2:
                week_str = col[1]
                try:
                    col_week = int(week_str.split()[0])
                    if col_week == week:
                        metric = week_str
                        try:
                            val = float(row[col])
                            if pd.notna(val):
                                if 'Gross' in metric:
                                    gross_val = val
                                elif 'Returns' in metric:
                                    returns_val = val
                                elif 'Net' in metric:
                                    net_val = val
                        except:
                            pass
                except:
                    pass
        
        if gross_val is None or returns_val is None:
            continue
        
        if gross_val > 0 or returns_val > 0:
            # Calculate return rate using Gross Sales
            return_rate = (returns_val / gross_val * 100) if gross_val > 0 else 0
            
            weekly_records.append({
                'Branch': current_branch,
                'SKU': sku_name,
                'Week': week,
                'Gross Sales': int(gross_val),
                'Returns': int(returns_val),
                'Net Sales': int(net_val) if net_val else int(gross_val - returns_val),
                'Return Rate': round(return_rate, 1)
            })

if len(weekly_records) > 0:
    weekly_df = pd.DataFrame(weekly_records)
    
    print(f"✅ Transformed to {len(weekly_df)} weekly SKU records")
    print(f"Branches: {weekly_df['Branch'].nunique()}")
    print(f"SKUs: {weekly_df['SKU'].nunique()}")
    print(f"Weeks: {sorted(weekly_df['Week'].unique())}")
    
    print(f"\nSample data:")
    print(weekly_df.head(30))
    
    # Save
    weekly_df.to_csv('data/october_weekly_sku_level.csv', index=False)
    print(f"\n✅ Saved to october_weekly_sku_level.csv")
else:
    print("\n❌ No records extracted!")
