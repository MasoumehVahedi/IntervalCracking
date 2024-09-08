import time
import pandas as pd
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt


def search(df, interval_queries):
    times = []
    for index, row in interval_queries.iterrows():
        start_date = row['start_date']
        end_date = row['end_date']
        start_time = time.time()
        matching_rows = df[(df['D.O.A'] >= start_date) & (df['D.O.A'] <= end_date)]
        end_time = time.time()
        total_time = end_time - start_time
        times.append(total_time)
        print(f"\nResults for query {index + 1} [{start_date} to {end_date}]: {len(matching_rows)} matching entries")
        #print(matching_rows[['D.O.A', 'D.O.D']])
    return times



if __name__ == "__main__":
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

    # Load the interval queries with start_date and end_date
    #interval_queries = pd.read_csv("interval_queries_30days_10K.csv")  # CPU time for scan = 6.02 seconds
    #interval_queries = pd.read_csv("interval_queries_7days_10K.csv")    # CPU time for scan = 5.005 seconds
    interval_queries = pd.read_csv("interval_queries_1day_10K.csv")     # CPU time for scan = 4.511 seconds
    #interval_queries = pd.read_csv("mixed_interval_queries_10K.csv")     # CPU time for scan = 5.220 seconds
    interval_queries['start_date'] = pd.to_datetime(interval_queries['start_date'], errors='coerce')
    interval_queries['end_date'] = pd.to_datetime(interval_queries['end_date'], errors='coerce')

    start_time = time.time()
    times = search(df, interval_queries)
    end_time = time.time()
    cpu_time = end_time - start_time
    print("CPU time for scan =", cpu_time, "seconds")

    np.save("scanTimes_1_day.npy", times)

    # Define the intervals you want to group the times into
    intervals = [(0, 10), (10, 40), (40, 70), (70, 100), (100, 500), (500, 1000)]


    # Calculate the average time for each interval
    def calculate_average_times(query_times, intervals):
        avg_times = []
        for start, end in intervals:
            avg_times.append(np.mean(query_times[start:end]))
        return avg_times


    query_times_avg = calculate_average_times(times, intervals)

    # Plot the times
    plt.plot([10 ** i for i in range(len(intervals))], query_times_avg, label='Rtree', marker='o', linestyle='-',
             color='indigo', markersize=10)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Query Number')
    plt.ylabel('Time (seconds)')
    plt.show()



