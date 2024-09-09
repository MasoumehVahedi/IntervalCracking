import matplotlib.pyplot as plt
import json

from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon



def get_mbb(sorted_cluster):
    # polygons is a list of the 100 polygons in the cluster
    polygons = [Polygon(coords) for coords in sorted_cluster]
    cluster = MultiPolygon(polygons)
    minx, miny, maxx, maxy = cluster.bounds
    mbb = [(minx, miny), (maxx, maxy)]
    return mbb


def calculate_bounding_box(rectangles):
    x_min = float('inf')
    y_min = float('inf')
    x_max = float('-inf')
    y_max = float('-inf')

    for polygon, rectangle in rectangles:
        x_min = min(x_min, rectangle[0])
        y_min = min(y_min, rectangle[1])
        x_max = max(x_max, rectangle[2])
        y_max = max(y_max, rectangle[3])
    mbb = [(x_min, y_min), (x_max, y_max)]
    return mbb


"""def calculate_bounding_box(rectangles):
    x_min = float('inf')
    y_min = float('inf')
    x_max = float('-inf')
    y_max = float('-inf')

    for rectangle in rectangles:
        x_min = min(x_min, rectangle[0])
        y_min = min(y_min, rectangle[1])
        x_max = max(x_max, rectangle[2])
        y_max = max(y_max, rectangle[3])
    mbb = [(x_min, y_min), (x_max, y_max)]
    return mbb"""



def saveTimes(file_name, query_times, cumulative_times):
    data = {
        "queryTimes": query_times,
        "cumulativeTimes": cumulative_times
    }
    with open(file_name, "w") as f:
        json.dump(data, f)


def loadTimes(file_name):
    with open(file_name, "r") as f:
        data = json.load(f)
    return data["queryTimes"], data["cumulativeTimes"]


def plot_cumulative_times(cumulative_times, label):
    plt.figure(figsize=(10, 6))
    plt.plot(cumulative_times, label=label)
    plt.xlabel("Number of Queries")
    plt.ylabel("Cumulative Time (seconds)")
    plt.title("Cumulative Query Response Time for 100K Range Queries")
    plt.yscale('log')  # Use logarithmic scale for y-axis if needed
    plt.legend()
    plt.grid(True)
    plt.show()

