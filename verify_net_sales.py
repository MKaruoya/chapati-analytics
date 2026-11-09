import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("Verifying Net Sales Calculation\n")
print("="*60)

october_weeks = [41, 42, 43, 44]
df_october = df[df['Week'].isin(october_weeks)].copy()

# Get CHANDARANA
chandarana = df_october[df_october['Branch'].str.contains('CHANDARANA', na=False)]

print("Checking if: Net Sales = Gross Sales - Returns\n")

all_match = True

for idx, row in chandarana.iterrows():
    branch = row['Branch']
    gross = row['Gross Sales']
    returns = row['Returns']
    net_stored = row['Net Sales']
    
    # Calculate what it should be
    net_calculated = gross - returns
    
    # Check if it matches
    match = "✅" if net_calculated == net_stored else "❌"
    
    if net_calculated != net_stored:
        all_match = False
        print(f"{match} {branch}")
        print(f"    Week: {row['Week']}")
        print(f"    Gross: {gross}, Returns: {returns}")
        print(f"    Stored Net: {net_stored}")
        print(f"    Calculated Net: {net_calculated}")
        print(f"    Difference: {net_stored - net_calculated}")
        print()

if all_match:
    print("✅ ALL NET SALES MATCH!")
    print("\nFormula confirmed: Net Sales = Gross Sales - Returns")
else:
    print("\n❌ SOME NET SALES DON'T MATCH!")
    print("There may be data quality issues")

print("\n" + "="*60)
print("Sample verification:")
sample = chandarana.head(5)
for idx, row in sample.iterrows():
    print(f"\n{row['Branch']} (Week {row['Week']})")
    print(f"  Gross: {row['Gross Sales']}")
    print(f"  Returns: {row['Returns']}")
    print(f"  Net (stored): {row['Net Sales']}")
    print(f"  Net (calculated): {row['Gross Sales'] - row['Returns']}")
