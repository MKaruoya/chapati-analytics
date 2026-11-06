import pandas as pd
from utils import add_month_to_weekly_data

print("Creating monthly dataset from weekly data (with Gross Sales)...\n")

# Load weekly data
weekly_df = pd.read_csv('data/october_weekly_with_gross.csv')

print(f"Weekly data shape: {weekly_df.shape}")
print(f"Branches: {weekly_df['Branch'].nunique()}")

# Add month column
weekly_df = add_month_to_weekly_data(weekly_df)

print(f"\nSample weekly data:")
print(weekly_df.head(10))

# Aggregate to monthly
monthly_data = []

for branch in sorted(weekly_df['Branch'].unique()):
    branch_data = weekly_df[weekly_df['Branch'] == branch]
    
    row = {'Branch': branch}
    
    # For each month 1-8
    for month in range(1, 9):
        month_data = branch_data[branch_data['Month'] == month]
        
        if len(month_data) > 0:
            gross = month_data['Gross Sales'].sum()
            returns = month_data['Returns'].sum()
            net = month_data['Net Sales'].sum()
        else:
            gross = 0
            returns = 0
            net = 0
        
        row[f'M{month}_Gross'] = int(gross)
        row[f'M{month}_Returns'] = int(returns)
        row[f'M{month}_Net'] = int(net)
    
    monthly_data.append(row)

final_df = pd.DataFrame(monthly_data)

print(f"\nMonthly data shape: {final_df.shape}")
print(f"Columns: {final_df.columns.tolist()}")

print(f"\nSample monthly data:")
print(final_df.head(10))

# Save
final_df.to_csv('data/october_dataset_with_gross.csv', index=False)
print(f"\n✅ Saved to october_dataset_with_gross.csv")
print(f"Total records: {len(final_df)}")
