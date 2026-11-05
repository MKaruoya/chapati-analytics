import pandas as pd

# Read raw with multi-level headers
df_raw = pd.read_csv('data/october_dataset.csv', header=[0, 1, 2])

print("Total columns:", len(df_raw.columns))
print("\nColumn structure (first 40):")
for i, col in enumerate(df_raw.columns[:40]):
    print(f"{i}: {col}")
