import pandas as pd

print("Verifying extraction accuracy\n")
print("="*60)

# Read raw
df_raw = pd.read_csv('data/October dataset 2.csv', header=None)

# Read extracted
df_extracted = pd.read_csv('data/october_weekly_correct.csv')

print("Checking a specific branch-week combination:\n")

# Find CHANDARANA ABC BRANCH, Week 43 in raw
print("Raw data for CHANDARANA ABC BRANCH:")
for row_idx in range(4, len(df_raw)):
    branch = df_raw.iloc[row_idx, 0]
    if pd.notna(branch) and 'ABC' in str(branch) and 'CHANDARANA' in str(branch):
        print(f"Found at row {row_idx}: {branch}")
        
        # Find Week 43 columns (Gross, Returns, Net)
        # Week 43 should be around column 205-207 based on pattern
        print(f"\nWeek 43 data from raw:")
        for col in range(200, 232):
            val = df_raw.iloc[1, col]
            if pd.notna(val) and '43' in str(val) and 'Gross' in str(val):
                gross = df_raw.iloc[row_idx, col]
                returns = df_raw.iloc[row_idx, col+1]
                net = df_raw.iloc[row_idx, col+2]
                print(f"  Gross: {gross}, Returns: {returns}, Net: {net}")
        break

print("\n\nExtracted data for CHANDARANA ABC BRANCH, Week 43:")
chandarana_abc_43 = df_extracted[(df_extracted['Branch'].str.contains('ABC', na=False)) & 
                                  (df_extracted['Week'] == 43)]
print(chandarana_abc_43[['Branch', 'Week', 'Gross Sales', 'Returns', 'Net Sales']])

print("\n\n" + "="*60)
print("Summary:")
print(f"✅ Extraction appears correct if values match above")
print(f"\nTotal extracted records: {len(df_extracted)}")
print(f"October records: {len(df_extracted[df_extracted['Week'].isin([41,42,43,44])])}")
print(f"October Gross Sales: {df_extracted[df_extracted['Week'].isin([41,42,43,44])]['Gross Sales'].sum():,}")
