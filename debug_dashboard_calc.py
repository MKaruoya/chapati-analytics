import pandas as pd

df = pd.read_csv('data/october_weekly_correct.csv')

october_weeks = [41, 42, 43, 44]
df_october = df[df['Week'].isin(october_weeks)].copy()

# Get CHANDARANA
chandarana = df_october[df_october['Branch'].str.contains('CHANDARANA', na=False)]

print("CHANDARANA Analysis\n")
print("="*60)

# Method 1: What dashboard does (average of branch rates)
branch_metrics = []
for branch in chandarana['Branch'].unique():
    branch_data = chandarana[chandarana['Branch'] == branch]
    gross = branch_data['Gross Sales'].sum()
    returns = branch_data['Returns'].sum()
    
    if gross > 0:
        rate = (returns / gross * 100)
        branch_metrics.append(rate)
        print(f"{branch}: {rate:.1f}%")

avg_of_branches = sum(branch_metrics) / len(branch_metrics)
print(f"\nMethod 1 (Average of branch rates): {avg_of_branches:.1f}%")

# Method 2: TRUE overall rate
total_gross = chandarana['Gross Sales'].sum()
total_returns = chandarana['Returns'].sum()
true_rate = (total_returns / total_gross * 100) if total_gross > 0 else 0

print(f"\nMethod 2 (TRUE overall rate):")
print(f"  Total Gross: {total_gross}")
print(f"  Total Returns: {total_returns}")
print(f"  Rate: {true_rate:.1f}%")

print(f"\n\nDifference: {avg_of_branches - true_rate:.1f}%")
print(f"\nWhy? Because averaging branch rates gives equal weight to each branch,")
print(f"even if some branches have much higher sales than others!")
