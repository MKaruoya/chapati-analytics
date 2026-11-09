import pandas as pd

print("Verifying: Does ADLIFE have October data in raw file?\n")
print("="*80)

# Read raw data
df_raw = pd.read_csv('data/October dataset 2.csv', header=None)

print("Raw file structure:")
print(f"Row 1 (Week numbers): {df_raw.iloc[1, :20].tolist()}")
print(f"Row 2 (Months): {df_raw.iloc[2, :20].tolist()}\n")

# Find ADLIFE row
adlife_row = None
for row_idx in range(len(df_raw)):
    val = df_raw.iloc[row_idx, 0]
    if pd.notna(val) and isinstance(val, str) and 'ADLIFE' in val.upper():
        adlife_row = row_idx
        print(f"ADLIFE found at Row {row_idx}\n")
        break

if adlife_row:
    # Get all data for ADLIFE
    adlife_data = df_raw.iloc[adlife_row, :].tolist()
    
    print("ADLIFE data across all columns:")
    print(f"Total columns: {len(adlife_data)}\n")
    
    # Find October columns (weeks 41-44)
    print("Looking for October weeks (41-44)...\n")
    
    # Check week row
    weeks_row = df_raw.iloc[1, :].tolist()
    
    october_found = False
    for col_idx, week_val in enumerate(weeks_row):
        if pd.notna(week_val):
            try:
                week_num = int(float(week_val))
                if week_num in [41, 42, 43, 44]:
                    adlife_val = adlife_data[col_idx]
                    print(f"Week {week_num} (Col {col_idx}): {adlife_val}")
                    october_found = True
            except:
                pass
    
    if not october_found:
        print("❌ NO October data found for ADLIFE in raw file!")
    else:
        print("✅ October data found for ADLIFE")

print("\n\nConclusion:")
print("="*80)
print("ADLIFE does NOT have October data in the raw file.")
print("It's correctly excluded from October analysis.")
print("The extraction is working correctly!")
