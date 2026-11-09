import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("Verifying October totals for CHANDARANA branches\n")
print("="*60)

october_weeks = [41, 42, 43, 44]
df_october = df[df['Week'].isin(october_weeks)].copy()

# Get CHANDARANA branches
chandarana = df_october[df_october['Branch'].str.contains('CHANDARANA', na=False)]

print(f"CHANDARANA branches in October:\n")

for branch in sorted(chandarana['Branch'].unique()):
    branch_data = chandarana[chandarana['Branch'] == branch]
    
    print(f"\n{branch}")
    print(f"  Weeks with data: {sorted(branch_data['Week'].unique())}")
    print(f"  Number of records: {len(branch_data)}")
    
    # Show each week
    for week in sorted(branch_data['Week'].unique()):
        week_data = branch_data[branch_data['Week'] == week]
        gross = week_data['Gross Sales'].sum()
        returns = week_data['Returns'].sum()
        print(f"    Week {week}: Gross {gross}, Returns {returns}")
    
    total_gross = branch_data['Gross Sales'].sum()
    total_returns = branch_data['Returns'].sum()
    print(f"  TOTAL: Gross {total_gross}, Returns {total_returns}")

print(f"\n\n" + "="*60)
print("CHANDARANA TOTAL October:")
total_gross = chandarana['Gross Sales'].sum()
total_returns = chandarana['Returns'].sum()
print(f"Gross Sales: {total_gross}")
print(f"Returns: {total_returns}")
print(f"Return Rate: {(total_returns/total_gross*100):.1f}%")
