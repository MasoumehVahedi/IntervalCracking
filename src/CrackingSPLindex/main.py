import time
import sys
import json
import os

import numpy as np

sys.path.append('../')

from ConfigParam import Config
from treeModel import TreeBuilder
from crackingSPLindex import CrackingSPLindex



def load_data(data_dir):
    # Read data
    polygons_path = os.path.join(data_dir, Config().water_polygon_name)
    polygons = np.load(polygons_path, allow_pickle=True)
    print(len(polygons))
    return polygons


def index_construction():
    print("-------- Loading data ---------")
    data_dir = "./"
    polygons = load_data(data_dir)

    print("-------- SPLindex building ---------")
    spli = CrackingSPLindex(polygons)
    clusters, cluster_labels = spli.clusters, spli.cluster_labels
    z_ranges_sorted, sorted_clusters_IDs, sorted_clusters = spli.sortClustersZaddress(clusters)
    all_mbr_z_intervals = spli.getZAddressesForMBRsInCluster(sorted_clusters)
    # Build the tree model
    tree = TreeBuilder(global_percentage=0.05, capacity_node=100)
    tree_model = tree.buildTreeModel(z_ranges_sorted, sorted_clusters_IDs)

    return spli, tree_model, all_mbr_z_intervals



def splindexRangeQuery(spli, tree_model, all_mbr_z_intervals, query_ranges):
    print("-------- Range Query ---------")
    for i, query_rect in enumerate(query_ranges, start=1):
        print(f"\nQuery {i}: Searching intervals that overlap with {query_rect}")
        query_results = spli.queryAdaptiveSPLindex(all_mbr_z_intervals, tree_model, query_rect)
        print(f"Final query result: {len(query_results)}")


def main():
    range_query_path = "./"
    query_path = os.path.join(range_query_path, Config().water_query_range_path)
    query_ranges = np.load(query_path, allow_pickle=True)
    ######## Building SPLindex ##########
    spli, tree_model, all_mbr_z_intervals = index_construction()

    ######## Range Query ##########
    start_cpu_time = time.time()
    splindexRangeQuery(spli, tree_model, all_mbr_z_intervals, query_ranges)
    end_cpu_time = time.time()
    cpu_time = end_cpu_time - start_cpu_time
    print("CPU time for CrackingSPLindex =", cpu_time, "seconds")


if __name__ == "__main__":
    main()