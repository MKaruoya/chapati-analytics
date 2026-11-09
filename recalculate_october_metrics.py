import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("CORRECTED October Metrics\n")
print("="*80)

october_weeks = [41, 42, 43, 44]
df_october = df[df['Week'].isin(october_weeks)]

print(f"Total October records: {len(df_october):,}")
print(f"Total branches with October data: {df_october['Branch'].nunique()}")

total_gross = df_october['Gross Sales'].sum()
total_returns = df_october['Returns'].sum()
total_net = df_october['Net Sales'].sum()

overall_return_rate = (total_returns / total_gross * 100) if total_gross > 0 else 0

print(f"\nOctober Totals (ALL STORES):")
print(f"  Gross Sales: {total_gross:,} units")
print(f"  Returns: {total_returns:,} units")
print(f"  Net Sales: {total_net:,} units")
print(f"  Overall Return Rate: {overall_return_rate:.2f}%")

print(f"\n\nComparison to OLD data:")
print(f"  Old October records: 151")
print(f"  New October records: {len(df_october):,}")
print(f"  Increase: {len(df_october) - 151} records ({((len(df_october) - 151) / 151 * 100):.0f}%)")

print(f"\n  Old branches: 112")
print(f"  New branches: {df_october['Branch'].nunique()}")
print(f"  Increase: {df_october['Branch'].nunique() - 112} branches")

print(f"\n\nBy Week:")
for week in sorted(df_october['Week'].unique()):
    week_data = df_october[df_october['Week'] == week]
    week_gross = week_data['Gross Sales'].sum()
    week_returns = week_data['Returns'].sum()
    week_rate = (week_returns / week_gross * 100) if week_gross > 0 else 0
    print(f"  Week {week}: {len(week_data):,} records, Gross {week_gross:,}, Returns {week_returns:,}, Rate {week_rate:.2f}%")

print(f"\n\nTop 10 outlets by October sales:")
outlets = df_october['Branch'].str.split('-').str[0].str.strip()
outlet_summary = []
for outlet in outlets.unique():
    outlet_data = df_october[df_october['Branch'].str.contains(outlet, na=False)]
    gross = outlet_data['Gross Sales'].sum()
    returns = outlet_data['Returns'].sum()
    rate = (returns / gross * 100) if gross > 0 else 0
    outlet_summary.append({
        'Outlet': outlet,
        'Gross': gross,
        'Returns': returns,
        'Rate': rate,
        'Branches': outlet_data['Branch'].nunique()
    })

outlet_df = pd.DataFrame(outlet_summary).sort_values('Gross', ascending=False)
print(outlet_df.head(10).to_string(index=False))
