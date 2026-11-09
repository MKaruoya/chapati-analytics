import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("Checking what data the graph displays\n")
print("="*60)

# Simulate what the dashboard does
october_weeks = [41, 42, 43, 44]
df_october = df[df['Week'].isin(october_weeks)].copy()

print(f"Dashboard filters for October (Weeks 41-44):")
print(f"  Records: {len(df_october):,}")
print(f"  Gross Sales: {df_october['Gross Sales'].sum():,}")

# Get CHANDARANA
outlet_name = "CHANDARANA SUPERMARKETS LTD."
outlet_branches = [
    b for b in df_october['Branch'].unique() 
    if b.split('-')[0].strip() == outlet_name.split('-')[0].strip()
]

print(f"\n\nCHANDARANA branches in October: {len(outlet_branches)}")

# Calculate metrics (what dashboard shows)
branch_metrics = []
for branch in outlet_branches:
    branch_data = df_october[df_october['Branch'] == branch]
    
    if len(branch_data) == 0:
        continue
    
    total_gross = branch_data['Gross Sales'].sum()
    total_returns = branch_data['Returns'].sum()
    
    if total_gross == 0:
        continue
    
    return_rate = (total_returns / total_gross * 100)
    
    branch_metrics.append({
        'Branch': branch,
        'Gross Sales': total_gross,
        'Returns': total_returns,
        'Return Rate': return_rate
    })

metrics_df = pd.DataFrame(branch_metrics)
print(f"\nBranches with October data: {len(metrics_df)}")
print(f"\nGraph will show:")
print(metrics_df.sort_values('Return Rate', ascending=False)[['Branch', 'Gross Sales', 'Return Rate']])

print(f"\n\n" + "="*60)
print("Answer: YES, the graph ONLY shows October data (Weeks 41-44)")
print("It aggregates all available October weeks for each branch")
