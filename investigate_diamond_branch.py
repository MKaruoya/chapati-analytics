import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("Investigating DIAMOND BRANCH data inconsistency\n")
print("="*60)

# Get DIAMOND branch
diamond = df[df['Branch'].str.contains('DIAMOND', na=False)]

print(f"Total DIAMOND records: {len(diamond)}")
print(f"All weeks: {sorted(diamond['Week'].unique())}")

print(f"\n\nOctober weeks (41-44):")
october_weeks = [41, 42, 43, 44]
diamond_oct = diamond[diamond['Week'].isin(october_weeks)]

print(f"Records: {len(diamond_oct)}")
print(diamond_oct[['Branch', 'Week', 'Gross Sales', 'Returns', 'Net Sales']])

print(f"\n\nAll DIAMOND data:")
print(diamond[['Branch', 'Week', 'Gross Sales', 'Returns', 'Net Sales']].sort_values('Week'))

print(f"\n\nCalculating October totals manually:")
oct_gross = diamond_oct['Gross Sales'].sum()
oct_returns = diamond_oct['Returns'].sum()
print(f"Gross: {oct_gross}, Returns: {oct_returns}")
if oct_gross > 0:
    print(f"Return Rate: {(oct_returns/oct_gross*100):.1f}%")
