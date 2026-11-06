from datetime import datetime, timedelta

# 2026 calendar - map week numbers to months
# Week 10 = March 9-15, 2026
# Week 52 = Dec 21-27, 2026

def get_month_from_week(week_num):
    """Convert ISO week number to month (2026)"""
    # Get a date in 2026 with the given ISO week
    jan_4_2026 = datetime(2026, 1, 4)
    week_1_monday = jan_4_2026 - timedelta(days=jan_4_2026.weekday())
    
    target_date = week_1_monday + timedelta(weeks=week_num - 1)
    return target_date.month

# Test mapping
print("Week to Month Mapping (2026):\n")
print("Week | Month | Date Range")
print("-" * 40)

for week in range(10, 45):
    month = get_month_from_week(week)
    jan_4_2026 = datetime(2026, 1, 4)
    week_1_monday = jan_4_2026 - timedelta(days=jan_4_2026.weekday())
    target_date = week_1_monday + timedelta(weeks=week - 1)
    end_date = target_date + timedelta(days=6)
    
    month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                   7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    
    print(f"{week:2d}   | M{month}    | {target_date.strftime('%b %d')} - {end_date.strftime('%b %d')}")
