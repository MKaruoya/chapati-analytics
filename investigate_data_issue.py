import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("Data Investigation\n")
print("="*60)

# Check all data
print(f"Total records: {len(df)}")
print(f"Total branches: {df['Branch'].nunique()}")
print(f"Total weeks: {df['Week'].nunique()}")

print(f"\n\nWeekly breakdown:")
for week in sorted(df['Week'].unique()):
    week_data = df[df['Week'] == week]
    total_gross = week_data['Gross Sales'].sum()
    print(f"Week {week}: {len(week_data)} records, Total Gross: {total_gross:,}")

print(f"\n\nOctober (Weeks 41-44):")
october_weeks = [41, 42, 43, 44]
october_data = df[df['Week'].isin(october_weeks)]
print(f"Total October records: {len(october_data)}")
print(f"Total October Gross Sales: {october_data['Gross Sales'].sum():,}")
print(f"Average per record: {october_data['Gross Sales'].mean():.1f}")

print(f"\n\nTop 10 branches by total sales:")
branch_totals = df.groupby('Branch')['Gross Sales'].sum().sort_values(ascending=False)
print(branch_totals.head(10))

print(f"\n\nCHANDARANA total sales:")
chandarana = df[df['Branch'].str.contains('CHANDARANA', na=False)]
print(f"Total: {chandarana['Gross Sales'].sum():,}")
print(f"By branch:")
print(chandarana.groupby('Branch')['Gross Sales'].sum().sort_values(ascending=False))

print(f"\n\nChecking if we're missing data...")
print(f"Branches with only 1 record: {len(df.groupby('Branch').size()[df.groupby('Branch').size() == 1])}")
print(f"Branches with 2-5 records: {len(df.groupby('Branch').size()[(df.groupby('Branch').size() >= 2) & (df.groupby('Branch').size() <= 5)])}")
print(f"Branches with 10+ records: {len(df.groupby('Branch').size()[df.groupby('Branch').size() >= 10])}")
