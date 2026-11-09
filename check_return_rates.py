import pandas as pd

df = pd.read_csv('data/october_weekly_sku_level.csv')

print("Return Rate Calculation Check\n")
print("="*60)

# Get a sample branch
sample_branch = 'CHANDARANA SUPERMARKETS LTD.-ABC BRANCH'
branch_data = df[df['Branch'] == sample_branch]

print(f"\nBranch: {sample_branch}")
print(f"Total records: {len(branch_data)}")

print(f"\nSample rows:")
print(branch_data[['Branch', 'SKU', 'Week', 'Gross Sales', 'Returns', 'Return Rate']].head(20))

print(f"\n\nAggregated totals:")
total_gross = branch_data['Gross Sales'].sum()
total_returns = branch_data['Returns'].sum()
calculated_rate = (total_returns / total_gross * 100) if total_gross > 0 else 0

print(f"Total Gross Sales: {total_gross}")
print(f"Total Returns: {total_returns}")
print(f"Calculated Return Rate: {calculated_rate:.1f}%")

print(f"\n\nAverage of Return Rate column:")
avg_return_rate = branch_data['Return Rate'].mean()
print(f"Average Return Rate: {avg_return_rate:.1f}%")

print(f"\n\nComparison:")
print(f"Method 1 (Total Returns / Total Gross): {calculated_rate:.1f}%")
print(f"Method 2 (Average of Return Rate column): {avg_return_rate:.1f}%")

print(f"\n\nSample calculation for one row:")
sample = branch_data.iloc[0]
print(f"Row: {sample['SKU']} Week {sample['Week']}")
print(f"Gross Sales: {sample['Gross Sales']}")
print(f"Returns: {sample['Returns']}")
print(f"Stored Return Rate: {sample['Return Rate']}")
manual_calc = (sample['Returns'] / sample['Gross Sales'] * 100) if sample['Gross Sales'] > 0 else 0
print(f"Manual calculation: {manual_calc:.1f}%")
