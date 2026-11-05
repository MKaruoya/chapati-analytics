import pandas as pd
from utils import calculate_monthly_metrics, get_active_periods, extract_outlet_name

# Load data
df = pd.read_csv('data/october_dataset_transformed.csv')
print("✅ Data loaded")
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}\n")

# Get branches
all_names = df['Branch'].dropna().unique()
print(f"✅ All branches: {len(all_names)}")
print(f"Sample: {list(all_names[:3])}\n")

# Filter valid branches
valid_branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
print(f"✅ Valid branches (with '-'): {len(valid_branches)}")
print(f"Sample: {valid_branches[:3]}\n")

# Get outlet names
outlet_names = sorted(set([extract_outlet_name(b) for b in valid_branches if extract_outlet_name(b)]))
print(f"✅ Outlet names: {len(outlet_names)}")
print(f"All outlets: {outlet_names}\n")

# Test with first outlet
if outlet_names:
    selected_outlet = outlet_names[0]
    print(f"Testing with outlet: {selected_outlet}")
    
    outlet_branches = [b for b in valid_branches if extract_outlet_name(b) == selected_outlet]
    print(f"Branches in this outlet: {len(outlet_branches)}")
    print(f"Sample: {outlet_branches[:3]}\n")
    
    # Get numeric columns
    numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
    print(f"✅ Numeric columns: {numeric_cols}\n")
    
    # Test calculate_monthly_metrics on first branch
    if outlet_branches:
        branch = outlet_branches[0]
        print(f"Testing with branch: {branch}")
        
        branch_row = df[df['Branch'] == branch]
        print(f"Branch row shape: {branch_row.shape}\n")
        
        monthly_data = calculate_monthly_metrics(branch_row, numeric_cols)
        print(f"✅ Monthly data calculated:")
        for m in monthly_data:
            print(f"  Month {m['month_num']}: has_data={m['has_data']}, sales={m['sales']}, returns={m['returns']}, return_rate={m['return_rate']:.1f}%")
        
        active_periods = get_active_periods(monthly_data)
        print(f"\n✅ Active periods: {len(active_periods)}")
        
        if active_periods:
            month_8 = monthly_data[7]
            print(f"\nMonth 8 data: {month_8}")
            print(f"Is active: {month_8['has_data']}")
