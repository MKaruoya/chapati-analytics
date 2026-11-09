import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("October Weekly Data Coverage\n")
print("="*60)

# Filter for October
october_weeks = [41, 42, 43, 44]
df_october = df[df['Week'].isin(october_weeks)].copy()

print(f"Total October records: {len(df_october)}")
print(f"Total branches with October data: {df_october['Branch'].nunique()}")

print(f"\n\nBranches WITHOUT October data:")
print("="*60)

all_branches = df['Branch'].unique()
branches_with_october = df_october['Branch'].unique()
branches_without_october = [b for b in all_branches if b not in branches_with_october]

print(f"Total branches in dataset: {len(all_branches)}")
print(f"Branches with October data: {len(branches_with_october)}")
print(f"Branches WITHOUT October data: {len(branches_without_october)}")

print(f"\n\nSample of branches without October data:")
for branch in branches_without_october[:20]:
    # Check what weeks they have
    branch_data = df[df['Branch'] == branch]
    weeks = sorted(branch_data['Week'].unique())
    print(f"  {branch}: Weeks {weeks}")

print(f"\n\nWhy no October data?")
print("="*60)
print("Possible reasons:")
print("1. Branch didn't report data for October (Weeks 41-44)")
print("2. Branch was closed/inactive in October")
print("3. Data entry error - data not submitted")
print("4. Branch is new - started after October")
print("5. Branch was delisted - no longer active")
