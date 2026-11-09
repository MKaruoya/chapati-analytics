import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("Investigating missing October data\n")
print("="*60)

# Check MAJID
majid = df[df['Branch'].str.contains('MAJID', na=False)]

print(f"Total MAJID records (all weeks): {len(majid)}")
print(f"Total MAJID branches: {majid['Branch'].nunique()}")

print(f"\n\nMAJID by week (all year):")
for week in sorted(majid['Week'].unique()):
    week_data = majid[majid['Week'] == week]
    print(f"Week {week}: {len(week_data)} records, Gross: {week_data['Gross Sales'].sum():,}")

print(f"\n\nOctober weeks (41-44) for MAJID:")
october_weeks = [41, 42, 43, 44]
majid_oct = majid[majid['Week'].isin(october_weeks)]

print(f"Total October records: {len(majid_oct)}")
print(f"Total October Gross: {majid_oct['Gross Sales'].sum():,}")

print(f"\n\nDetailed October breakdown:")
for week in october_weeks:
    week_data = majid_oct[majid_oct['Week'] == week]
    print(f"\nWeek {week}: {len(week_data)} records")
    print(week_data[['Branch', 'Gross Sales', 'Returns']].to_string())

print(f"\n\nCompare to other weeks:")
print(f"Week 40 (before October): {majid[majid['Week'] == 40]['Gross Sales'].sum():,}")
print(f"Week 39: {majid[majid['Week'] == 39]['Gross Sales'].sum():,}")
print(f"Week 38: {majid[majid['Week'] == 38]['Gross Sales'].sum():,}")

print(f"\n\nAre we missing branches in October?")
majid_branches = majid['Branch'].unique()
majid_oct_branches = majid_oct['Branch'].unique()
print(f"Total MAJID branches: {len(majid_branches)}")
print(f"MAJID branches in October: {len(majid_oct_branches)}")
print(f"Missing from October: {len(majid_branches) - len(majid_oct_branches)}")
