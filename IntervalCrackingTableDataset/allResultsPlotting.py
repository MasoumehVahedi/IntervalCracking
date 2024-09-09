import numpy as np
import matplotlib.pyplot as plt


# Load the data for each model
query_times_model1 = np.load("scanTimes_mixed.npy", allow_pickle=True)
query_times_model2 = np.load("crackingTimes_30_days.npy", allow_pickle=True)
query_times_model3 = np.load("crackingTimes_7_days.npy", allow_pickle=True)
query_times_model4 = np.load("crackingTimes_1_day.npy", allow_pickle=True)
query_times_model5 = np.load("crackingTimes_mixed.npy", allow_pickle=True)

# Define the specific query count intervals (logarithmic scale)
intervals = [(0, 3), (4, 10), (10, 100), (100, 1000), (1000, 10000)]

# Calculate the average time for each interval
def calculate_average_times(query_times, intervals):
    avg_times = []
    for start, end in intervals:
        avg_times.append(np.mean(query_times[start:end]))
    return avg_times

query_times_model1_avg = calculate_average_times(query_times_model1, intervals)
query_times_model2_avg = calculate_average_times(query_times_model2, intervals)
query_times_model3_avg = calculate_average_times(query_times_model3, intervals)
query_times_model4_avg = calculate_average_times(query_times_model4, intervals)
query_times_model5_avg = calculate_average_times(query_times_model5, intervals)

# Plot the data
plt.figure(figsize=(8, 5))

# Plot each model's average data with distinct markers and lines
#plt.plot([10**i for i in range(len(intervals))], query_times_model1_avg, label='Sequential Search', linestyle='-', color='indigo', linewidth=2)
plt.axhline(y=np.mean(query_times_model1), color='indigo', linestyle='-', linewidth=2, label='Sequential Search')
plt.plot([10**i for i in range(len(intervals))], query_times_model2_avg, label='30-day Range Cracking', marker='s', linestyle='-', color='darkgreen', markersize=10)
plt.plot([10**i for i in range(len(intervals))], query_times_model3_avg, label='7-day Range Cracking', marker='^', linestyle='-', color='brown', markersize=10)
plt.plot([10**i for i in range(len(intervals))], query_times_model4_avg, label='1-day Range Cracking', marker='H', linestyle='-', color='darkorange', markersize=10)
plt.plot([10**i for i in range(len(intervals))], query_times_model5_avg, label='Mixed Cracking', marker='D', linestyle='-', color='royalblue', markersize=10)

plt.xlim(1, 10001)
plt.xscale('log')
plt.yscale('log')
plt.yticks(fontsize=22)

# Labels and title
plt.xlabel("Number of queries", fontsize=24)
plt.ylabel("Time", fontsize=24)
plt.legend(loc='upper right', ncol=1, fontsize=14)

plt.xticks([10**i for i in range(len(intervals))], ['$10^0$', '$10^1$', '$10^2$', '$10^3$', '$10^4$'], fontsize=22)

plt.tight_layout()
plt.show()