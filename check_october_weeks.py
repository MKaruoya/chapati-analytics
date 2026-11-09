import pandas as pd
from utils import get_month_from_week

df = pd.read_csv('data/october_weekly_branch_level.csv')

print("Weeks in dataset and their months:\n")

weeks = sorted(df['Week'].unique())
for week in weeks:
    month = get_month_from_week(week)
    month_names = {1: 'March', 2: 'April', 3: 'May', 4: 'June', 5: 'July', 6: 'August', 7: 'September', 8: 'October'}
    month_name = month_names.get(month, 'Unknown')
    print(f"Week {week}: Month {month} ({month_name})")

print(f"\n\nOctober weeks (Month 8):")
october_weeks = [w for w in weeks if get_month_from_week(w) == 8]
print(f"October weeks: {october_weeks}")
