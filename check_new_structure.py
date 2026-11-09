import pandas as pd

print("Analyzing new October dataset 2...\n")

# Read raw to see structure
df_raw = pd.read_csv('data/October dataset 2.csv', header=None)

print(f"Raw shape: {df_raw.shape}")
print(f"\nFirst 5 rows (first 15 columns):")
print(df_raw.iloc[:5, :15])

print(f"\n\nFirst column (Branch names):")
print(df_raw.iloc[3:20, 0].tolist())
