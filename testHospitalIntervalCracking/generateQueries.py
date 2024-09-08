import pandas as pd
import numpy as np
from datetime import timedelta, datetime


################# Generate queries 30 days intervals #############
"""df = pd.read_csv("shuffled_HDHI.csv")
df['D.O.A'] = pd.to_datetime(df['D.O.A'], errors='coerce')
df['D.O.D'] = pd.to_datetime(df['D.O.D'], errors='coerce')

print(df.head())
# Print the number of rows with missing 'D.O.A' and 'D.O.D'
print(f"Rows with missing 'D.O.A': {df['D.O.A'].isna().sum()}")
print(f"Rows with missing 'D.O.D': {df['D.O.D'].isna().sum()}")

# Remove rows where 'D.O.A' is NaT (missing admission dates)
df = df.dropna(subset=['D.O.A'])
# Calculate the average hospitalization period for rows where D.O.D is available
average_stay = (df['D.O.D'] - df['D.O.A']).dt.days.mean()
# Impute missing D.O.D using D.O.A + average_stay
df['D.O.D'].fillna(df['D.O.A'] + pd.to_timedelta(average_stay, unit='D'), inplace=True)


# Use both D.O.A and D.O.D to determine the global min/max date range
min_global_date = df['D.O.A'].min()
max_global_date = df['D.O.D'].max() if df['D.O.D'].notna().any() else df['D.O.A'].max()

n_queries = 10000
interval_queries = []

for _ in range(n_queries):
    # Generate a random start date within the dataset's date range
    delta_days = (max_global_date - min_global_date).days
    start_date = min_global_date + timedelta(days=np.random.randint(0, delta_days))
    end_date = min(start_date + timedelta(days=30), max_global_date)
    interval_queries.append([start_date, end_date])

interval_queries_df = pd.DataFrame(interval_queries, columns=['start_date', 'end_date'])
interval_queries_df.to_csv('interval_queries_30days_10K.csv', index=False)
print(interval_queries_df.head())"""



################# Generate queries for 7 days (weekly intervals) #############
"""df = pd.read_csv("shuffled_HDHI.csv")
df['D.O.A'] = pd.to_datetime(df['D.O.A'], errors='coerce')
df['D.O.D'] = pd.to_datetime(df['D.O.D'], errors='coerce')

print(df.head())
# Print the number of rows with missing 'D.O.A' and 'D.O.D'
print(f"Rows with missing 'D.O.A': {df['D.O.A'].isna().sum()}")
print(f"Rows with missing 'D.O.D': {df['D.O.D'].isna().sum()}")

# Remove rows where 'D.O.A' is NaT (missing admission dates)
df = df.dropna(subset=['D.O.A'])
# Calculate the average hospitalization period for rows where D.O.D is available
average_stay = (df['D.O.D'] - df['D.O.A']).dt.days.mean()
# Impute missing D.O.D using D.O.A + average_stay
df['D.O.D'].fillna(df['D.O.A'] + pd.to_timedelta(average_stay, unit='D'), inplace=True)


# Use both D.O.A and D.O.D to determine the global min/max date range
min_global_date = df['D.O.A'].min()
max_global_date = df['D.O.D'].max() if df['D.O.D'].notna().any() else df['D.O.A'].max()

n_queries = 10000
weekly_interval_queries = []

for _ in range(n_queries):
    # Generate a random start date within the dataset's date range
    start_date = min_global_date + timedelta(days=np.random.randint(0, (max_global_date - min_global_date).days))
    # End date is 7 days after the start date
    end_date = min(start_date + timedelta(days=7), max_global_date)
    weekly_interval_queries.append([start_date, end_date])

# Convert to a DataFrame and save to CSV
weekly_interval_queries_df = pd.DataFrame(weekly_interval_queries, columns=['start_date', 'end_date'])
weekly_interval_queries_df.to_csv('interval_queries_7days_10K.csv', index=False)
print(weekly_interval_queries_df.head())"""



################# Generate queries for one-day intervals #############
"""df = pd.read_csv("shuffled_HDHI.csv")
df['D.O.A'] = pd.to_datetime(df['D.O.A'], errors='coerce')
df['D.O.D'] = pd.to_datetime(df['D.O.D'], errors='coerce')

print(df.head())
# Print the number of rows with missing 'D.O.A' and 'D.O.D'
print(f"Rows with missing 'D.O.A': {df['D.O.A'].isna().sum()}")
print(f"Rows with missing 'D.O.D': {df['D.O.D'].isna().sum()}")

# Remove rows where 'D.O.A' is NaT (missing admission dates)
df = df.dropna(subset=['D.O.A'])
# Calculate the average hospitalization period for rows where D.O.D is available
average_stay = (df['D.O.D'] - df['D.O.A']).dt.days.mean()
# Impute missing D.O.D using D.O.A + average_stay
df['D.O.D'].fillna(df['D.O.A'] + pd.to_timedelta(average_stay, unit='D'), inplace=True)

# Use both D.O.A and D.O.D to determine the global min/max date range
min_global_date = df['D.O.A'].min()
max_global_date = df['D.O.D'].max() if df['D.O.D'].notna().any() else df['D.O.A'].max()

n_queries = 10000
one_day_interval_queries = []

for _ in range(n_queries):
    # Generate a random start date within the dataset's date range
    start_date = min_global_date + timedelta(days=np.random.randint(0, (max_global_date - min_global_date).days))
    # End date is the same as start date (one day interval)
    end_date = start_date
    one_day_interval_queries.append([start_date, end_date])

# Convert to a DataFrame and save to CSV
one_day_interval_queries_df = pd.DataFrame(one_day_interval_queries, columns=['start_date', 'end_date'])
one_day_interval_queries_df.to_csv('interval_queries_1day_10K.csv', index=False)
print(one_day_interval_queries_df.head())"""


################# Generate a mixture of interval queries (30 days, 7 days, 1 day) #############
df = pd.read_csv("shuffled_HDHI.csv")
df['D.O.A'] = pd.to_datetime(df['D.O.A'], errors='coerce')
df['D.O.D'] = pd.to_datetime(df['D.O.D'], errors='coerce')

print(df.head())
# Print the number of rows with missing 'D.O.A' and 'D.O.D'
print(f"Rows with missing 'D.O.A': {df['D.O.A'].isna().sum()}")
print(f"Rows with missing 'D.O.D': {df['D.O.D'].isna().sum()}")

# Remove rows where 'D.O.A' is NaT (missing admission dates)
df = df.dropna(subset=['D.O.A'])
# Calculate the average hospitalization period for rows where D.O.D is available
average_stay = (df['D.O.D'] - df['D.O.A']).dt.days.mean()
# Impute missing D.O.D using D.O.A + average_stay
df['D.O.D'].fillna(df['D.O.A'] + pd.to_timedelta(average_stay, unit='D'), inplace=True)


# Use both D.O.A and D.O.D to determine the global min/max date range
min_global_date = df['D.O.A'].min()
max_global_date = df['D.O.D'].max() if df['D.O.D'].notna().any() else df['D.O.A'].max()

n_queries = 10000
mixed_interval_queries = []

for _ in range(n_queries):
    # Randomly choose the type of interval: 1 for daily, 7 for weekly, 30 for monthly
    interval_type = int(np.random.choice([1, 7, 30]))  # Convert numpy int64 to standard Python int
    start_date = min_global_date + timedelta(days=np.random.randint(0, (max_global_date - min_global_date).days))

    end_date = min(start_date + timedelta(days=interval_type), max_global_date)
    mixed_interval_queries.append([start_date, end_date])

# Convert to a DataFrame and save to CSV
mixed_interval_queries_df = pd.DataFrame(mixed_interval_queries, columns=['start_date', 'end_date'])
mixed_interval_queries_df.to_csv('mixed_interval_queries_10K.csv', index=False)
print(mixed_interval_queries_df.head())


