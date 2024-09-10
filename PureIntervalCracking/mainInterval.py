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
    data_dir = "./"
    polygons_path = os.path.join(data_dir, Config().water_polygon_name)
    polygons = np.load(polygons_path, allow_pickle=True)
    
    range_query_path = "./"
    query_path = os.path.join(range_query_path, Config().water_query_range_path)
    query_ranges = np.load(query_path, allow_pickle=True)
    
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
    print("CPU time for pure interval cracking =", cpu_time, "seconds")


if __name__ == "__main__":
    main()