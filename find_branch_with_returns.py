import pandas as pd

df = pd.read_csv('data/october_dataset_transformed.csv')

print("Looking for branches with return data...\n")

count = 0
for idx, branch in df.iterrows():
    branch_name = branch['Branch']
    
    # Check if any month has returns
    has_returns = False
    for i in range(1, 9):
        if branch[f'M{i}_Returns'] > 0:
            has_returns = True
            break
    
    if has_returns:
        print(f"\n{branch_name}:")
        for i in range(1, 9):
            returns = branch[f'M{i}_Returns']
            sales = branch[f'M{i}_Sales']
            if returns > 0 or sales > 0:
                order_qty = sales + returns
                return_rate = (returns / order_qty * 100) if order_qty > 0 else 0
                print(f"  M{i}: Sales={sales}, Returns={returns}, Return%={return_rate:.1f}%")
        
        count += 1
        if count >= 5:
            break
