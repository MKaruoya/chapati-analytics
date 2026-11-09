import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("Detailed investigation: CHANDARANA ADLIFE BRANCH\n")
print("="*80)

adlife = df[df['Branch'].str.contains('ADLIFE', na=False)]

print(f"Total records: {len(adlife)}")
print(f"Weeks: {sorted(adlife['Week'].unique())}\n")

print("All records:")
print(adlife[['Branch', 'Week', 'Gross Sales', 'Returns', 'Net Sales', 'Return Rate']].to_string())

print(f"\n\nSummary:")
total_gross = adlife['Gross Sales'].sum()
total_returns = adlife['Returns'].sum()
total_net = adlife['Net Sales'].sum()

print(f"Total Gross Sales: {total_gross}")
print(f"Total Returns: {total_returns}")
print(f"Total Net Sales: {total_net}")

if total_gross > 0:
    return_rate = (total_returns / total_gross * 100)
    print(f"Return Rate: {return_rate:.1f}%")

print(f"\n\nWeek breakdown:")
for week in sorted(adlife['Week'].unique()):
    week_data = adlife[adlife['Week'] == week]
    gross = week_data['Gross Sales'].sum()
    returns = week_data['Returns'].sum()
    if gross > 0:
        rate = (returns / gross * 100)
    else:
        rate = 0
    print(f"Week {week}: Gross {gross}, Returns {returns}, Rate {rate:.1f}%")

print(f"\n\nLast week with data: Week {adlife['Week'].max()}")
print(f"October weeks: 41, 42, 43, 44")
print(f"Missing October? {adlife['Week'].max() < 41}")
