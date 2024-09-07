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
    path = "shuffled_HDHI.csv"
    df = pd.read_csv(path)
    df['D.O.A'] = pd.to_datetime(df['D.O.A'], errors='coerce', format='%d/%m/%Y')
    df['D.O.D'] = pd.to_datetime(df['D.O.D'], errors='coerce', format='%d/%m/%Y')

    # Load the interval queries with start_date and end_date
    #interval_queries = pd.read_csv("interval_queries_30days_10K.csv")  # CPU time for scan = 5.929571866989136 seconds
    #interval_queries = pd.read_csv("interval_queries_7days_10K.csv")    # CPU time for scan = 5.029099702835083 seconds
    #interval_queries = pd.read_csv("interval_queries_1day_10K.csv")     # CPU time for scan = 4.654155015945435 seconds
    interval_queries = pd.read_csv("mixed_interval_queries_10K.csv")     # CPU time for scan = 5.349354982376099 seconds
    interval_queries['start_date'] = pd.to_datetime(interval_queries['start_date'], errors='coerce')
    interval_queries['end_date'] = pd.to_datetime(interval_queries['end_date'], errors='coerce')

    start_time = time.time()
    times = search(df, interval_queries)
    end_time = time.time()
    cpu_time = end_time - start_time
    print("CPU time for scan =", cpu_time, "seconds")

    np.save("scanTimes_mixed.npy", times)

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



