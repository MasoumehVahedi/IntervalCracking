import numpy as np
import time
import sys

sys.path.append('../')

from IntervalCracking import Interval, IntervalCracking
from ZAdress import MortonCode


def getMBR(polygon):
    return np.array(polygon.bounds)


def getZAddressesForMBRsInCluster(polygons):
    mbr_z_intervals = []
    for mbr in polygons:
        zmin = MortonCode().interleave_latlng(mbr[1], mbr[0])  # miny, minx
        zmax = MortonCode().interleave_latlng(mbr[3], mbr[2])  # maxy, maxx
        if zmin > zmax:
            zmin, zmax = zmax, zmin  # Swap if out of order
        mbr_z_intervals.append([(zmin, zmax), mbr])
    return mbr_z_intervals


def main():
    #polygons_path = "/Users/vahedi/Library/CloudStorage/OneDrive-RoskildeUniversitet/Python Projects/AdaptiveSPLindex/DebuggingAdaptiveSPLindex/water_poly.npy"
    polygons_path = "/Users/vahedi/Library/CloudStorage/OneDrive-RoskildeUniversitet/Python Projects/AdaptiveSPLindex/MYFINALCrackingSPLindex/roads_mbrs_float.txt"
    #polygons_path = "/Users/vahedi/Library/CloudStorage/OneDrive-RoskildeUniversitet/Python Projects/AdaptiveSPLindex/MYFINALCrackingSPLindex/lakes.npy"
    #polygons = np.load(polygons_path, allow_pickle=True)[:100000]
    polygons = np.loadtxt(polygons_path)[:10000000]
    print(len(polygons))
    #query_path = "/Users/vahedi/Library/CloudStorage/OneDrive-RoskildeUniversitet/Python Projects/AdaptiveSPLindex/DebuggingAdaptiveSPLindex/query_ranges_5M_10k.npy"
    #query_path = "/Users/vahedi/Library/CloudStorage/OneDrive-RoskildeUniversitet/Python Projects/AdaptiveSPLindex/DebuggingAdaptiveSPLindex/query_ranges_5M_10k.npy"
    #query_path = "/Users/vahedi/Library/CloudStorage/OneDrive-RoskildeUniversitet/Python Projects/AdaptiveSPLindex/DebuggingAdaptiveSPLindex/expanded_lakes_mbrs.npy"
    query_path = "/Users/vahedi/Library/CloudStorage/OneDrive-RoskildeUniversitet/Python Projects/AdaptiveSPLindex/MYFINALCrackingSPLindex/usa_e-2%_uniform_1m_other_float.txt"
    #query_ranges = np.load(query_path, allow_pickle=True)[:1000]
    print("query_ranges = ", len(query_ranges))

    start_cpu_time = time.time()
    mbr_z_intervals = getZAddressesForMBRsInCluster(polygons)
    index = IntervalCracking(mbr_z_intervals)

    ######## Range Query ##########
    for i, query in enumerate(query_ranges):
        zmin = MortonCode().interleave_latlng(query[1], query[0])
        zmax = MortonCode().interleave_latlng(query[3], query[2])
        query_interval = Interval(zmin, zmax)

        results = index.adaptiveSearch(query_interval, query)
        print(f"Query {i} results: {len(results)}")

    # Print the tree structure after the queries
    #tree_structure = index.print_tree()
    #for line in tree_structure:
    #    print(line)

    end_cpu_time = time.time()
    cpu_time = end_cpu_time - start_cpu_time
    print("CPU time for AdaptiveSPLindex =", cpu_time, "seconds")


if __name__ == "__main__":
    main()