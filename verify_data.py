import pandas as pd

df = pd.read_csv('data/october_dataset_transformed.csv')

# Get first branch
branch = df.iloc[0]
print(f"Branch: {branch['Branch']}")
print("\nMonthly data:")
for i in range(1, 9):
    returns = branch[f'M{i}_Returns']
    sales = branch[f'M{i}_Sales']
    order_qty = sales + returns
    return_rate = (returns / order_qty * 100) if order_qty > 0 else 0
    print(f"M{i}: Sales={sales}, Returns={returns}, Order={order_qty}, Return%={return_rate:.1f}%")
