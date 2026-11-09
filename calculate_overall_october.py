import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("Overall October Return Rate - ALL STORES\n")
print("="*60)

# Filter for October only (Weeks 41-44)
october_weeks = [41, 42, 43, 44]
df_october = df[df['Week'].isin(october_weeks)].copy()

print(f"October data summary:")
print(f"  Total records: {len(df_october):,}")
print(f"  Total branches: {df_october['Branch'].nunique()}")
print(f"  Weeks: {sorted(df_october['Week'].unique())}")

print(f"\n\nOctober Totals (ALL STORES):")
print("="*60)

total_gross = df_october['Gross Sales'].sum()
total_returns = df_october['Returns'].sum()
total_net = df_october['Net Sales'].sum()

overall_return_rate = (total_returns / total_gross * 100) if total_gross > 0 else 0

print(f"Total Gross Sales:  {total_gross:,} units")
print(f"Total Returns:      {total_returns:,} units")
print(f"Total Net Sales:    {total_net:,} units")
print(f"\nOVERALL RETURN RATE: {overall_return_rate:.2f}%")

print(f"\n\nBreakdown by week:")
print("="*60)

for week in sorted(df_october['Week'].unique()):
    week_data = df_october[df_october['Week'] == week]
    week_gross = week_data['Gross Sales'].sum()
    week_returns = week_data['Returns'].sum()
    week_rate = (week_returns / week_gross * 100) if week_gross > 0 else 0
    
    print(f"Week {week}: Gross {week_gross:,}, Returns {week_returns:,}, Rate {week_rate:.2f}%")

print(f"\n\nBreakdown by outlet:")
print("="*60)

outlets = df_october['Branch'].str.split('-').str[0].str.strip().unique()

for outlet in sorted(outlets):
    outlet_data = df_october[df_october['Branch'].str.contains(outlet, na=False)]
    outlet_gross = outlet_data['Gross Sales'].sum()
    outlet_returns = outlet_data['Returns'].sum()
    outlet_rate = (outlet_returns / outlet_gross * 100) if outlet_gross > 0 else 0
    
    print(f"{outlet}: Gross {outlet_gross:,}, Returns {outlet_returns:,}, Rate {outlet_rate:.2f}%")

print(f"\n\nFormula used:")
print("="*60)
print(f"Overall Return Rate = (Total Returns / Total Gross Sales) × 100")
print(f"Overall Return Rate = ({total_returns:,} / {total_gross:,}) × 100")
print(f"Overall Return Rate = {overall_return_rate:.2f}%")
