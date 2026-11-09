import pandas as pd

df = pd.read_csv('data/october_weekly_sku_level.csv')

print("Checking for data quality issues\n")

# Check for negative or zero gross sales
print("Rows with Gross Sales <= 0:")
problem_rows = df[df['Gross Sales'] <= 0]
print(f"Count: {len(problem_rows)}")
if len(problem_rows) > 0:
    print(problem_rows[['Branch', 'SKU', 'Week', 'Gross Sales', 'Returns', 'Return Rate']].head(10))

print(f"\n\nRows with Returns > Gross Sales:")
problem_rows2 = df[df['Returns'] > df['Gross Sales']]
print(f"Count: {len(problem_rows2)}")
if len(problem_rows2) > 0:
    print(problem_rows2[['Branch', 'SKU', 'Week', 'Gross Sales', 'Returns', 'Return Rate']].head(10))

print(f"\n\nStatistics:")
print(f"Min Gross Sales: {df['Gross Sales'].min()}")
print(f"Max Gross Sales: {df['Gross Sales'].max()}")
print(f"Min Returns: {df['Returns'].min()}")
print(f"Max Returns: {df['Returns'].max()}")
print(f"Max Return Rate: {df['Return Rate'].max()}")
