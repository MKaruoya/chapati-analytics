import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("Investigating: Do branches without October data have sales but NO returns?\n")
print("="*80)

# Get branches without October data
october_weeks = [41, 42, 43, 44]
df_october = df[df['Week'].isin(october_weeks)]
branches_with_october = df_october['Branch'].unique()

all_branches = df['Branch'].unique()
branches_without_october = [b for b in all_branches if b not in branches_with_october]

print(f"Branches without October data: {len(branches_without_october)}\n")

# Check if they have sales but no returns in October
print("Checking if they have October sales but no returns...\n")

# Get ALL data for these branches (all weeks)
branches_data = df[df['Branch'].isin(branches_without_october)]

print(f"Total records for branches without October: {len(branches_data)}")
print(f"Total Gross Sales: {branches_data['Gross Sales'].sum():,}")
print(f"Total Returns: {branches_data['Returns'].sum():,}")

# Check if any have zero returns
zero_return_branches = branches_data[branches_data['Returns'] == 0]
print(f"\nRecords with ZERO returns: {len(zero_return_branches)}")
print(f"Percentage: {(len(zero_return_branches) / len(branches_data) * 100):.1f}%")

# Check average return rate
avg_return_rate = (branches_data['Returns'].sum() / branches_data['Gross Sales'].sum() * 100) if branches_data['Gross Sales'].sum() > 0 else 0
print(f"\nAverage return rate (all data): {avg_return_rate:.1f}%")

# Compare to branches WITH October data
branches_with_oct_data = df[df['Branch'].isin(branches_with_october)]
avg_return_rate_with_oct = (branches_with_oct_data['Returns'].sum() / branches_with_oct_data['Gross Sales'].sum() * 100) if branches_with_oct_data['Gross Sales'].sum() > 0 else 0

print(f"Average return rate (branches WITH October): {avg_return_rate_with_oct:.1f}%")

print(f"\n\nDifference: {avg_return_rate - avg_return_rate_with_oct:.1f}%")

if avg_return_rate < avg_return_rate_with_oct:
    print("✅ YES! Branches without October data have LOWER return rates!")
    print("   They might have been excluded because they had no returns to report.")
else:
    print("❌ NO. Return rates are similar.")

# Sample some branches
print(f"\n\nSample branches without October data:")
print("="*80)

for branch in branches_without_october[:5]:
    branch_data = df[df['Branch'] == branch]
    total_gross = branch_data['Gross Sales'].sum()
    total_returns = branch_data['Returns'].sum()
    
    if total_gross > 0:
        return_rate = (total_returns / total_gross * 100)
    else:
        return_rate = 0
    
    print(f"\n{branch}")
    print(f"  Total records: {len(branch_data)}")
    print(f"  Total Gross: {total_gross:,}")
    print(f"  Total Returns: {total_returns:,}")
    print(f"  Return Rate: {return_rate:.1f}%")
    print(f"  Weeks: {sorted(branch_data['Week'].unique())}")
