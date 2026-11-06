import pandas as pd

# Load weekly data
weekly_df = pd.read_csv('data/october_weekly_actual.csv')

print("Branches with Returns:\n")

# Get branches with returns
branches_with_returns = weekly_df[weekly_df['Returns'] > 0]['Branch'].unique()

print(f"Total branches: {weekly_df['Branch'].nunique()}")
print(f"Branches with returns: {len(branches_with_returns)}\n")

# Show sample branches with returns
print("Sample branches with returns:")
for branch in branches_with_returns[:10]:
    branch_data = weekly_df[weekly_df['Branch'] == branch]
    total_sales = branch_data['Sales'].sum()
    total_returns = branch_data['Returns'].sum()
    return_rate = (total_returns / (total_sales + total_returns) * 100) if (total_sales + total_returns) > 0 else 0
    
    print(f"\n{branch}")
    print(f"  Sales: {total_sales}, Returns: {total_returns}, Return Rate: {return_rate:.1f}%")

# Check for MAJID
print("\n" + "="*60)
print("Looking for MAJID branches:\n")

majid_branches = [b for b in weekly_df['Branch'].unique() if 'MAJID' in b.upper()]

if majid_branches:
    for branch in majid_branches:
        branch_data = weekly_df[weekly_df['Branch'] == branch]
        total_sales = branch_data['Sales'].sum()
        total_returns = branch_data['Returns'].sum()
        return_rate = (total_returns / (total_sales + total_returns) * 100) if (total_sales + total_returns) > 0 else 0
        
        print(f"\n{branch}")
        print(f"  Sales: {total_sales}, Returns: {total_returns}, Return Rate: {return_rate:.1f}%")
        print(f"  Weekly breakdown:")
        print(branch_data[['Week', 'Sales', 'Returns']].to_string())
else:
    print("No MAJID branches found")
    print("\nAll unique branches:")
    for branch in sorted(weekly_df['Branch'].unique())[:20]:
        print(f"  - {branch}")
