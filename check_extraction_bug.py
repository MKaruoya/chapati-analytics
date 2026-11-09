import pandas as pd

print("Checking extraction bug: ADLIFE in raw vs extracted\n")
print("="*80)

# Read raw data
df_raw = pd.read_csv('data/October dataset 2.csv', header=None)

print("Raw data (October dataset 2.csv):")
print(f"Shape: {df_raw.shape}")
print(f"Rows: {len(df_raw)}, Columns: {len(df_raw.columns)}\n")

# Find ADLIFE in raw
print("Searching for ADLIFE in raw data...")
for row_idx in range(len(df_raw)):
    for col_idx in range(len(df_raw.columns)):
        val = df_raw.iloc[row_idx, col_idx]
        if pd.notna(val) and isinstance(val, str) and 'ADLIFE' in val.upper():
            print(f"Found at Row {row_idx}, Col {col_idx}: {val}")
            # Show surrounding data
            print(f"  Row data: {df_raw.iloc[row_idx, :10].tolist()}")

print("\n\nExtracted data (october_weekly_correct.csv):")
df_extracted = pd.read_csv('data/october_weekly_correct.csv')

adlife_extracted = df_extracted[df_extracted['Branch'].str.contains('ADLIFE', na=False)]
print(f"ADLIFE records in extracted: {len(adlife_extracted)}")

if len(adlife_extracted) > 0:
    print(adlife_extracted[['Branch', 'Week', 'Gross Sales', 'Returns']])
else:
    print("NO ADLIFE DATA IN EXTRACTED FILE!")

print("\n\nConclusion:")
print("="*80)
print("If ADLIFE is in raw but not in extracted:")
print("→ The extraction script missed it")
print("→ Need to check extraction logic")
print("→ Possible issue: Column mapping or filtering")
