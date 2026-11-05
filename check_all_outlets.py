import pandas as pd
from utils import extract_outlet_name

df = pd.read_csv('data/october_dataset_transformed.csv')

valid_branches = [name for name in df['Branch'].unique() if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
outlet_names = sorted(set([extract_outlet_name(b) for b in valid_branches if extract_outlet_name(b)]))

print("ALL outlet names:")
for i, o in enumerate(outlet_names, 1):
    print(f"{i}. '{o}'")
