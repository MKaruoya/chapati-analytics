import pandas as pd

df = pd.read_csv('data/october_dataset_transformed.csv')

branches = df['Branch'].unique()
majid_branches = [b for b in branches if 'MAJID' in str(b).upper()]

print("Raw branch names from CSV:")
for b in majid_branches[:3]:
    print(f"  '{b}'")
    
# Check if there's a period
if majid_branches:
    first = majid_branches[0]
    print(f"\nFirst branch ends with period: {first.endswith('.')}")
    print(f"First branch: '{first}'")
