import json
import numpy as np
import matplotlib.pyplot as plt


# Load the data for each model
query_times_model1 = np.load("ScanTimes.npy", allow_pickle=True)
query_times_model2 = np.load("crackingTimes.npy", allow_pickle=True)

# Define the specific query count intervals (logarithmic scale)
intervals = [(0, 10), (10, 100), (100, 1000), (1000, 10000)]

def calculate_average_times(query_times, intervals):
    avg_times = []
    for start, end in intervals:
        avg_times.append(np.mean(query_times[start:end]))
    return avg_times


query_times_model1_avg = calculate_average_times(query_times_model1, intervals)
query_times_model2_avg = calculate_average_times(query_times_model2, intervals)


# Plot the data
plt.figure(figsize=(7, 5))

# Plot each model's average data with distinct markers and lines
plt.plot([10**i for i in range(len(intervals))], query_times_model1_avg, label='SimpleScan', marker='o', linestyle='-', color='indigo', markersize=10)
plt.plot([10**i for i in range(len(intervals))], query_times_model2_avg, label='IntervalCracking', marker='s', linestyle='--', color='darkgreen', markersize=10)

# Set log scale for both axes
plt.xscale('log')
plt.yscale('log')
plt.yticks(fontsize=22)

# Labels and title
plt.xlabel("Number of queries", fontsize=24)
plt.ylabel("Time", fontsize=24)
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, fontsize=14)
# Set specific x-ticks (10^1, 10^2, 10^3, 10^4, 10^5)
plt.xticks([10**i for i in range(len(intervals))], ['$10^1$', '$10^2$', '$10^3$', '$10^4$'], fontsize=22)

plt.tight_layout()
plt.show()
