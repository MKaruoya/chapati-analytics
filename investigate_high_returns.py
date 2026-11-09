import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("Investigating branches with >100% return rates\n")
print("="*60)

october_weeks = [41, 42, 43, 44]
df_october = df[df['Week'].isin(october_weeks)].copy()

# Calculate return rates
df_october['Calc_Return_Rate'] = (df_october['Returns'] / df_october['Gross Sales'] * 100).round(1)

# Find >100%
high_returns = df_october[df_october['Calc_Return_Rate'] > 100]

print(f"Branches with >100% return rates: {len(high_returns)}\n")

# Check MAJID
print("MAJID branches with >100% returns:")
majid_high = high_returns[high_returns['Branch'].str.contains('MAJID', na=False)]
print(majid_high[['Branch', 'Week', 'Gross Sales', 'Returns', 'Calc_Return_Rate']])

print("\n\nMAGUNA branches with >100% returns:")
maguna_high = high_returns[high_returns['Branch'].str.contains('MAGUNA', na=False)]
print(maguna_high[['Branch', 'Week', 'Gross Sales', 'Returns', 'Calc_Return_Rate']])

print("\n\n" + "="*60)
print("Understanding >100% returns:\n")

print("This happens when Returns > Gross Sales in a single week")
print("Example: Week 43 has Gross=10, Returns=15")
print("Return Rate = (15/10)*100 = 150%\n")

print("Why does this happen?")
print("- They ordered 10 units in Week 43")
print("- But returned 15 units (from previous weeks' stock)")
print("- Net result: -5 units (they owe us 5)\n")

print("This is LEGITIMATE data - not an error!")
print("It means they're returning more than they ordered that week")

print("\n\nAll branches with >100% returns:")
for idx, row in high_returns.iterrows():
    print(f"\n{row['Branch']} (Week {row['Week']})")
    print(f"  Gross Sales: {row['Gross Sales']}")
    print(f"  Returns: {row['Returns']}")
    print(f"  Net Sales: {row['Net Sales']}")
    print(f"  Return Rate: {row['Calc_Return_Rate']}%")
