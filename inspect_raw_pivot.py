import pandas as pd

print("Inspecting raw pivot table structure\n")

# Read without headers to see raw structure
df_raw = pd.read_csv('data/October dataset 2.csv', header=None)

print(f"Shape: {df_raw.shape}")
print(f"\nFirst 10 rows, first 20 columns:")
print(df_raw.iloc[:10, :20])

print(f"\n\nRow 3 (headers):")
print(df_raw.iloc[3, :20].tolist())

print(f"\n\nRow 4 (first data row):")
print(df_raw.iloc[4, :20].tolist())

print(f"\n\nLooking for a specific branch-SKU combination:")
# Find CHANDARANA ABC BRANCH
for idx in range(5, 50):
    val = df_raw.iloc[idx, 0]
    if pd.notna(val) and 'ABC' in str(val):
        print(f"\nRow {idx}: {val}")
        print(df_raw.iloc[idx, :20].tolist())
        break
