import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("Branches WITHOUT October Data\n")
print("="*80)

# Filter for October
october_weeks = [41, 42, 43, 44]
df_october = df[df['Week'].isin(october_weeks)]

# Get all branches
all_branches = sorted(df['Branch'].unique())
branches_with_october = df_october['Branch'].unique()
branches_without_october = [b for b in all_branches if b not in branches_with_october]

print(f"Total branches in dataset: {len(all_branches)}")
print(f"Branches WITH October data: {len(branches_with_october)}")
print(f"Branches WITHOUT October data: {len(branches_without_october)}\n")

print("="*80)
print("BRANCHES WITHOUT OCTOBER DATA:\n")

for i, branch in enumerate(branches_without_october, 1):
    # Get what weeks they have
    branch_data = df[df['Branch'] == branch]
    weeks = sorted(branch_data['Week'].unique())
    latest_week = max(weeks)
    
    print(f"{i}. {branch}")
    print(f"   Weeks available: {weeks}")
    print(f"   Latest week: {latest_week}")
    print()

# Summary by outlet
print("\n" + "="*80)
print("SUMMARY BY OUTLET:\n")

outlet_summary = {}
for branch in branches_without_october:
    outlet = branch.split('-')[0].strip() if '-' in branch else branch
    if outlet not in outlet_summary:
        outlet_summary[outlet] = 0
    outlet_summary[outlet] += 1

for outlet in sorted(outlet_summary.keys()):
    print(f"{outlet}: {outlet_summary[outlet]} branches without October data")

print(f"\nTotal: {len(branches_without_october)} branches without October data")
