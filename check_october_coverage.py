import pandas as pd

df = pd.read_csv('data/october_weekly_branch_level.csv')

# Filter for October (Weeks 41-44)
october_weeks = [41, 42, 43, 44]
df_october = df[df['Week'].isin(october_weeks)].copy()

print("October Data Coverage Check\n")
print("="*60)

# Get CHANDARANA branches
chandarana = df_october[df_october['Branch'].str.contains('CHANDARANA', na=False)]

print(f"Total CHANDARANA branches: {chandarana['Branch'].nunique()}")
print(f"\nBranches and their week coverage:\n")

for branch in sorted(chandarana['Branch'].unique()):
    branch_data = chandarana[chandarana['Branch'] == branch]
    weeks = sorted(branch_data['Week'].unique())
    total_gross = branch_data['Gross Sales'].sum()
    total_returns = branch_data['Returns'].sum()
    
    print(f"{branch}")
    print(f"  Weeks: {weeks}")
    print(f"  Week count: {len(weeks)}/4")
    print(f"  Total Gross: {total_gross}, Total Returns: {total_returns}")
    print()

print("\n" + "="*60)
print("Summary:")
print(f"Expected: 4 weeks (41, 42, 43, 44)")
print(f"Branches with 4 weeks: {len(chandarana[chandarana.groupby('Branch')['Week'].transform('nunique') == 4]['Branch'].unique())}")
print(f"Branches with <4 weeks: {len(chandarana[chandarana.groupby('Branch')['Week'].transform('nunique') < 4]['Branch'].unique())}")
