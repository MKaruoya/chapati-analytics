import pandas as pd

print("Analyzing column structure\n")

df_raw = pd.read_csv('data/October dataset 2.csv', header=None)

print("Row 0 (Month/Week labels):")
print(df_raw.iloc[0, :30].tolist())

print("\n\nRow 1 (Week numbers):")
print(df_raw.iloc[1, :30].tolist())

print("\n\nRow 2 (Month names):")
print(df_raw.iloc[2, :30].tolist())

print("\n\nRow 3 (Metrics):")
print(df_raw.iloc[3, :30].tolist())

print("\n\nPattern analysis:")
print("Looking for repeating pattern of (Gross, Returns, Net)...\n")

for col in range(1, 30):
    metric = df_raw.iloc[3, col]
    if pd.notna(metric):
        print(f"Col {col}: {metric}")
