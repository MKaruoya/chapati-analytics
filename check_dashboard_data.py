import pandas as pd
import os

print("Checking Dashboard Data Source\n")
print("="*60)

# Check which file the upload page is trying to load
file_path = os.path.join('data', 'october_weekly_correct.csv')

print(f"File path: {file_path}")
print(f"File exists: {os.path.exists(file_path)}")

if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    
    print(f"\n✅ File loaded successfully!")
    print(f"\nData Summary:")
    print(f"  Total records: {len(df):,}")
    print(f"  Columns: {df.columns.tolist()}")
    print(f"  Branches: {df['Branch'].nunique()}")
    print(f"  Weeks: {sorted(df['Week'].unique())}")
    
    print(f"\n\nOctober data (Weeks 41-44):")
    october_weeks = [41, 42, 43, 44]
    df_oct = df[df['Week'].isin(october_weeks)]
    print(f"  October records: {len(df_oct):,}")
    print(f"  October Gross Sales: {df_oct['Gross Sales'].sum():,}")
    print(f"  October branches: {df_oct['Branch'].nunique()}")
    
    print(f"\n\nSample data:")
    print(df.head(10))
    
else:
    print(f"\n❌ File NOT found!")
    print(f"\nAvailable files in data/:")
    for file in os.listdir('data'):
        print(f"  - {file}")
