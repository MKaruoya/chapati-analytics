import pandas as pd

df = pd.read_csv('data/october_weekly_with_gross.csv')

print("Data Structure:")
print(f"Shape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nFirst 20 rows:")
print(df.head(20))

print(f"\n\nUnique Branches: {df['Branch'].nunique()}")
print(f"Branches: {df['Branch'].unique()}")

print(f"\n\nWeeks: {sorted(df['Week'].unique())}")

print(f"\n\nSample for one branch (CHANDARANA):")
chandarana = df[df['Branch'] == 'CHANDARANA SUPERMARKETS LTD.']
print(chandarana[['Branch', 'Week', 'Gross Sales', 'Returns', 'Return Rate']].head(20))
