import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("Return Rate Calculation Logic in Dashboard\n")
print("="*60)

october_weeks = [41, 42, 43, 44]
df_october = df[df['Week'].isin(october_weeks)].copy()

# Simulate dashboard logic
chandarana = df_october[df_october['Branch'].str.contains('CHANDARANA', na=False)]

print("Dashboard does this for each branch:\n")

for branch in sorted(chandarana['Branch'].unique())[:5]:
    branch_data = chandarana[chandarana['Branch'] == branch]
    
    # This is what the dashboard code does (from pages/dashboard.py line ~115)
    oct_gross = branch_data['Gross Sales'].sum()
    oct_returns = branch_data['Returns'].sum()
    oct_net = branch_data['Net Sales'].sum()
    
    if oct_gross == 0:
        continue
    
    # RETURN RATE CALCULATION
    oct_return_rate = (oct_returns / oct_gross * 100)
    
    print(f"{branch}")
    print(f"  Step 1: Sum all Gross Sales = {oct_gross}")
    print(f"  Step 2: Sum all Returns = {oct_returns}")
    print(f"  Step 3: Calculate = (Returns / Gross) * 100")
    print(f"  Step 4: ({oct_returns} / {oct_gross}) * 100 = {oct_return_rate:.1f}%")
    print()

print("\n" + "="*60)
print("FORMULA USED:")
print("\nReturn Rate = (Total Returns / Total Gross Sales) * 100")
print("\nThis is the CORRECT method!")
print("It gives the true return percentage for the period")
