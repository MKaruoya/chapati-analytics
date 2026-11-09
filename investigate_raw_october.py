import pandas as pd

print("Investigating raw October dataset 2 for complete data\n")
print("="*60)

# Read raw without headers
df_raw = pd.read_csv('data/October dataset 2.csv', header=None)

print(f"Raw file shape: {df_raw.shape}")
print(f"Total rows: {len(df_raw)}")

# Find CHANDARANA ABC BRANCH row
print("\n\nSearching for CHANDARANA ABC BRANCH in raw data...\n")

for idx in range(len(df_raw)):
    val = df_raw.iloc[idx, 0]
    if pd.notna(val) and 'ABC' in str(val) and 'CHANDARANA' in str(val):
        print(f"Found at row {idx}: {val}")
        print(f"\nAll columns for this row:")
        row_data = df_raw.iloc[idx, :].tolist()
        for col_idx, col_val in enumerate(row_data):
            if pd.notna(col_val):
                print(f"  Col {col_idx}: {col_val}")
        break

print("\n\n" + "="*60)
print("Checking column headers (Row 3):\n")
headers = df_raw.iloc[3, :].tolist()
for col_idx, header in enumerate(headers[:30]):
    if pd.notna(header):
        print(f"Col {col_idx}: {header}")

print("\n\nLooking for all October data (weeks 41-44)...")
print("Checking if raw file has data for weeks 41, 42, 43, 44\n")

# Check headers for week numbers
for col_idx in range(len(headers)):
    header = str(headers[col_idx])
    if any(str(w) in header for w in [41, 42, 43, 44]):
        print(f"Col {col_idx}: {header}")
