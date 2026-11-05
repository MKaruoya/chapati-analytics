import pandas as pd

df = pd.read_csv('data/october_dataset_transformed.csv')

# Find MAJID branches
majid_branches = [b for b in df['Branch'].unique() if 'MAJID' in str(b).upper()]

print(f"MAJID branches found: {len(majid_branches)}")
print("\nAll MAJID branches:")
for b in majid_branches:
    print(f"  {b}")

if majid_branches:
    print("\n\nData for first MAJID branch:")
    branch = majid_branches[0]
    branch_data = df[df['Branch'] == branch].iloc[0]
    print(f"\nBranch: {branch}")
    print(f"M1_Returns: {branch_data['M1_Returns']}")
    print(f"M1_Sales: {branch_data['M1_Sales']}")
    print(f"M8_Returns: {branch_data['M8_Returns']}")
    print(f"M8_Sales: {branch_data['M8_Sales']}")
    
    # Check all months
    print("\n\nAll months:")
    for i in range(1, 9):
        returns_col = f'M{i}_Returns'
        sales_col = f'M{i}_Sales'
        print(f"M{i}: Returns={branch_data[returns_col]}, Sales={branch_data[sales_col]}")
