import numpy as np


polygons_path = "/Users/vahedi/Library/CloudStorage/OneDrive-RoskildeUniversitet/Python Projects/AdaptiveSPLindex/MYFINALCrackingSPLindex/roads_mbrs_float.txt"
polygons = np.loadtxt(polygons_path)[:100]
print(polygons)

query_path = "/Users/vahedi/Library/CloudStorage/OneDrive-RoskildeUniversitet/Python Projects/AdaptiveSPLindex/DebuggingAdaptiveSPLindex/query_ranges_roads_1000.npy"
query_ranges = np.load(query_path, allow_pickle=True)[:10]
print(query_ranges)