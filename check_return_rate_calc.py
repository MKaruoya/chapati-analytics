import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

print("Checking Return Rate Calculation\n")
print("="*60)

october_weeks = [41, 42, 43, 44]
df_october = df[df['Week'].isin(october_weeks)].copy()

# Get CHANDARANA
chandarana = df_october[df_october['Branch'].str.contains('CHANDARANA', na=False)]

print("Method 1: Dashboard calculation (what we're doing now)\n")

for branch in sorted(chandarana['Branch'].unique())[:3]:
    branch_data = chandarana[chandarana['Branch'] == branch]
    
    total_gross = branch_data['Gross Sales'].sum()
    total_returns = branch_data['Returns'].sum()
    
    if total_gross > 0:
        calc_return_rate = (total_returns / total_gross * 100)
        
        print(f"{branch}")
        print(f"  Total Gross: {total_gross}")
        print(f"  Total Returns: {total_returns}")
        print(f"  Calculation: ({total_returns} / {total_gross}) * 100 = {calc_return_rate:.1f}%")
        print()

print("\n" + "="*60)
print("Method 2: Average of weekly return rates\n")

for branch in sorted(chandarana['Branch'].unique())[:3]:
    branch_data = chandarana[chandarana['Branch'] == branch]
    
    avg_return_rate = branch_data['Return Rate'].mean()
    
    print(f"{branch}")
    print(f"  Weekly return rates: {branch_data['Return Rate'].tolist()}")
    print(f"  Average: {avg_return_rate:.1f}%")
    print()

print("\n" + "="*60)
print("Which method is correct?")
print("\nMethod 1 (Total Returns / Total Gross) = CORRECT")
print("This is the true return rate for the period")
print("\nMethod 2 (Average of weekly rates) = WRONG")
print("This can be skewed by weeks with low sales")
