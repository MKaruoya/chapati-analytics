import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("NAIVAS October Sales Analysis\n")
print("="*60)

# Filter for NAIVAS
naivas = df[df['Branch'].str.contains('NAIVAS', na=False)]

print(f"Total NAIVAS branches: {naivas['Branch'].nunique()}")
print(f"\nAll NAIVAS branches:")
print(naivas['Branch'].unique())

# Filter for October only
october_weeks = [41, 42, 43, 44]
naivas_october = naivas[naivas['Week'].isin(october_weeks)]

print(f"\n\nOctober data for NAIVAS:")
print(f"Total October records: {len(naivas_october)}")
print(f"Branches with October data: {naivas_october['Branch'].nunique()}")

print(f"\n\nOctober breakdown by branch:")
october_summary = naivas_october.groupby('Branch').agg({
    'Gross Sales': 'sum',
    'Returns': 'sum',
    'Net Sales': 'sum',
    'Week': 'nunique'
}).round(1)

october_summary['Return Rate'] = (october_summary['Returns'] / october_summary['Gross Sales'] * 100).round(1)
october_summary = october_summary.rename(columns={'Week': 'Weeks'})
october_summary = october_summary.sort_values('Gross Sales', ascending=False)

print(october_summary)

print(f"\n\nTotal NAIVAS October:")
total_gross = naivas_october['Gross Sales'].sum()
total_returns = naivas_october['Returns'].sum()
total_net = naivas_october['Net Sales'].sum()
total_rate = (total_returns / total_gross * 100) if total_gross > 0 else 0

print(f"Gross Sales: {total_gross:,}")
print(f"Returns: {total_returns:,}")
print(f"Net Sales: {total_net:,}")
print(f"Return Rate: {total_rate:.1f}%")

print(f"\n\nComparing to dashboard data shown:")
print(f"Dashboard shows UTAWALA: Gross 107, Returns 11")
print(f"Our October data for UTAWALA:")
utawala_oct = naivas_october[naivas_october['Branch'].str.contains('UTAWALA', na=False)]
print(utawala_oct[['Branch', 'Week', 'Gross Sales', 'Returns', 'Net Sales']])
