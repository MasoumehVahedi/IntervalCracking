import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta, datetime
from revisedIntervalCracking import AdaptiveSPLindex, Interval

############ Interval Cracking ###########
"""
For each record in your dataset:
   1- D.O.A will be the starting date of the interval.
   2- D.O.D will be the ending date of the interval.
"""


def days_since_reference(date, reference_date):
    return (date - reference_date).days


def intervalCracking(df, interval_queries):
    intervals = []
    for index, row in df.iterrows():
        start_date = row['D.O.A']
        end_date = row['D.O.D'] if pd.notna(row['D.O.D']) else start_date

        # Convert dates to integer (days since reference)
        start_day = days_since_reference(start_date, reference_date)
        end_day = days_since_reference(end_date, reference_date)

        intervals.append([[start_day, end_day], index])

    # Now pass all intervals into AdaptiveSPLindex at once
    adaptive_index = AdaptiveSPLindex(intervals=intervals, FIRST_INIT=0,
                                      END_INIT=(df['D.O.D'].max() - reference_date).days)

    times = []
    for index, row in interval_queries.iterrows():
        start_date = row['start_date']
        end_date = row['end_date']

        # Convert the query interval into integer (days since reference)
        start_day = days_since_reference(start_date, reference_date)
        end_day = days_since_reference(end_date, reference_date)

        # Define the interval query using the integer representation
        query_interval = Interval(start_day, end_day)
        start_time = time.time()
        results = adaptive_index.adaptiveSearch(query_interval)
        end_time = time.time()
        total_time = end_time - start_time
        times.append(total_time)
        print(f"Results for query {index + 1} [{start_day} to {end_day}]: {len(results)} matching entries")

    return times



if __name__ == "__main__":
    df = pd.read_csv("shuffled_HDHI.csv")
    df['D.O.A'] = pd.to_datetime(df['D.O.A'], errors='coerce', format='%d/%m/%Y')
    df['D.O.D'] = pd.to_datetime(df['D.O.D'], errors='coerce', format='%d/%m/%Y')

    # Remove rows where 'D.O.A' is NaT (missing values)
    df = df.dropna(subset=['D.O.A'])
    reference_date = df['D.O.A'].min()

    #interval_queries = pd.read_csv("interval_queries_30days_10K.csv")  # CPU time for scan = 3.0115809440612793 seconds
    #interval_queries = pd.read_csv("interval_queries_7days_10K.csv")   # CPU time for cracking = 2.5223469734191895 seconds
    #interval_queries = pd.read_csv("interval_queries_1day_10K.csv")     # CPU time for cracking = 2.3298821449279785 seconds
    interval_queries = pd.read_csv("mixed_interval_queries_10K.csv")     # CPU time for cracking = 2.5149221420288086 seconds
    interval_queries['start_date'] = pd.to_datetime(interval_queries['start_date'], errors='coerce', format='%Y-%m-%d')
    interval_queries['end_date'] = pd.to_datetime(interval_queries['end_date'], errors='coerce', format='%Y-%m-%d')

    start_time = time.time()
    times = intervalCracking(df, interval_queries)
    end_time = time.time()
    cpu_time = end_time - start_time
    print("CPU time for cracking =", cpu_time, "seconds")

    np.save("crackingTimes_mixed.npy", times)

    # Define the intervals you want to group the times into
    intervals = [(0, 10), (10, 40), (40, 70), (70, 100), (100, 500), (500, 1000)]

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
