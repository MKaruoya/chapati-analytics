import pandas as pd

# Load the weekly data
weekly_df = pd.read_csv('data/october_weekly_actual.csv')

# Find branches with returns
branches_with_returns = weekly_df[weekly_df['Returns'] > 0]['Branch'].unique()

print(f"Branches with returns: {len(branches_with_returns)}\n")

# Show first branch with returns
if len(branches_with_returns) > 0:
    branch = branches_with_returns[0]
    print(f"Branch: {branch}\n")
    
    branch_data = weekly_df[weekly_df['Branch'] == branch]
    print(branch_data.to_string())
    
    print(f"\n\nMonthly totals for this branch:")
    for month in branch_data['Month'].unique():
        month_data = branch_data[branch_data['Month'] == month]
        sales = month_data['Sales'].sum()
        returns = month_data['Returns'].sum()
        order = sales + returns
        return_rate = (returns / order * 100) if order > 0 else 0
        print(f"M{int(month)}: Sales={sales}, Returns={returns}, Return Rate={return_rate:.1f}%")
