"""
   The SPLindex class contains cracking approach in "queryAdaptiveSPLindex" method that build and grow Interval Tree data structure incrementally.
   Here is some explaination of How the Tree Data Structure is Saved and Reused:

   1- Cluster Indices Dictionary:
    - SPLindex.cluster_indices is a class-level dictionary where each key is a cluster_id, and the value is an instance of IntervalCracking.
    - The IntervalCracking instance contains the tree data structure (Interval-tree) for the corresponding cluster.

   2- Saving the Tree Structure:
    - When a cluster is queried for the first time, the intervals for that cluster are loaded into an IntervalCracking instance.
    - This IntervalCracking instance builds an Interval-tree as queries are processed.
    - The instance is then stored in SPLindex.cluster_indices under the key corresponding to the cluster_id.

    3- Reusing the Tree Structure:
     - For subsequent queries on the same cluster, the code checks if the cluster_id already exists in SPLindex.cluster_indices.
     - If it exists, it retrieves the IntervalCracking instance (which contains the Interval-tree) and uses it to perform the query, instead of building the tree from scratch.
"""



import os
import sys
import logging
import numpy as np
from sklearn.cluster import Birch

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from IntervalCracking.interval_structures import Interval
from IntervalCracking.intervalCracking import IntervalCracking

#from IntervalCracking.improvedIntervalCracking import IntervalCracking, Interval
from ConfigParam import Config
from ZAdress import MortonCode
from helpers import calculate_bounding_box

logging.basicConfig(level=logging.DEBUG)



class CrackingSPLindex:
    ##### Static Variables #####
    _instance = None  # Singleton instance tracker
    cluster_indices = {}  # Maps cluster_id to CrackingSPLindex instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, polygons):
        if not hasattr(self, 'initialized'):
            self.polygons = polygons
            self.config = Config()
            self.morton_encoder = MortonCode()
            self.X = np.array([self.getMBR(polygon) for polygon in self.polygons], dtype=np.float32)
            self.clusters, self.cluster_labels = self.getClusters()
            self.initialized = True

    def getMBR(self, polygon):
        # bounds = (minx, miny, maxx, maxy)
        return np.array(polygon.bounds)

    def getClusters(self):
        birch = Birch(branching_factor=self.config.bf, n_clusters=self.config.n_clusters,
                      threshold=self.config.threshold).fit(self.X)
        self.cluster_labels = birch.labels_
        self.num_clusters = len(set(self.cluster_labels))
        print('Number of clusters:', self.num_clusters)
        self.clusters = [
            [(polygon, rectangle) for polygon, rectangle in
             zip(self.polygons[self.cluster_labels == n], self.X[self.cluster_labels == n])] for n in
            range(self.num_clusters)]
        return self.clusters, self.cluster_labels

    def getZAddressesForMBRsInCluster(self, sorted_clusters):
        all_mbr_z_intervals = {}
        for j, cluster in enumerate(sorted_clusters):
            mbr_z_intervals = []
            for (original_polygon, mbr) in cluster:  # minimum bounding region (minx, miny, maxx, maxy)
                zmin = MortonCode().interleave_latlng(mbr[1], mbr[0])  # miny, minx
                zmax = MortonCode().interleave_latlng(mbr[3], mbr[2])  # maxy, maxx
                # Ensure zmin is always less than zmax
                if zmin > zmax:
                    zmin, zmax = zmax, zmin
                mbr_z_intervals.append([(zmin, zmax), mbr])
            all_mbr_z_intervals[j] = mbr_z_intervals

        return all_mbr_z_intervals


    def sortClustersZaddress(self, clusters):
        MBR_clusters = []
        for i, cluster in enumerate(clusters):
            mbb = calculate_bounding_box(cluster)
            if np.all(np.isfinite(mbb)):
                MBR_clusters.append(mbb)

        self.all_z_addresses = []
        for mbr in MBR_clusters:
            z_addresses = [(MortonCode().interleave_latlng(mbr[0][1], mbr[0][0])),
                           (MortonCode().interleave_latlng(mbr[1][1], mbr[1][0]))]
            self.all_z_addresses.append(z_addresses)

        z_ranges_sorted = sorted(self.all_z_addresses, key=lambda x: x[0])
        sorted_indices = [self.all_z_addresses.index(c) for c in z_ranges_sorted]
        sorted_clusters = [self.clusters[i] for i in sorted_indices]
        sorted_clusters_IDs = [i for i, _ in enumerate(sorted_clusters)]
        return z_ranges_sorted, sorted_clusters_IDs, sorted_clusters


    def predClusterIdsRangeQuery(self, node, z_range):
        if node.leaf_model is not None:
            for (z_min, z_max), cluster_id in zip(node.z_ranges, node.clusters):
                if z_min <= z_range[1] and z_max >= z_range[0]:
                    yield (cluster_id, 1 / len(node.labels))
        else:
            if node.internal_model is not None and node.z_ranges[0][0] <= z_range[0] and node.z_ranges[-1][1] >= \
                    z_range[1]:
                X = np.array([[z_range[0], z_range[1]]])
                probs = node.internal_model.predict(X).flatten()
                left_cluster_probs = list(self.predClusterIdsRangeQuery(node.left_child, z_range))
                right_cluster_probs = list(self.predClusterIdsRangeQuery(node.right_child, z_range))

                for cluster_id in node.labels:
                    left_prob = sum(p for c_id, p in left_cluster_probs if c_id == cluster_id)
                    right_prob = sum(p for c_id, p in right_cluster_probs if c_id == cluster_id)
                    prob = probs[cluster_id] + left_prob + right_prob
                    yield (cluster_id, prob)
            else:
                if node.left_child and node.left_child.z_ranges[-1][1] >= z_range[0]:
                    yield from self.predClusterIdsRangeQuery(node.left_child, z_range)
                if node.right_child and node.right_child.z_ranges[0][0] <= z_range[1]:
                    yield from self.predClusterIdsRangeQuery(node.right_child, z_range)


    def queryAdaptiveSPLindex(self, all_mbr_z_intervals, model, query):
        """
           This function takes a query and then predict clusters and crack them.

          - Parameters:
            1- all_mbr_z_intervals: is a dictionary that holds the initial intervals for each cluster.
            2- model: the learned index model (SPLindex)
            3- For each query, clusters are predicted based on the query range using a model.

          - Building the Tree:
            If a cluster is queried for the first time, its intervals are loaded into an IntervalCracking.
            The IntervalCracking is stored in "SPLindex.cluster_indices" and is reused for subsequent queries on the same cluster.

          - Querying:
            When a query is made, the method checks if the cluster's tree exists in SPLindex.cluster_indices.
            If it exists, it uses the existing tree to quickly find results.
            If it doesn’t exist, it creates the tree for the cluster and then queries it.

        - Efficiency:
            The tree structure is built and refined over multiple queries, making the search more efficient over time.
            Subsequent queries on the same cluster use the refined tree, reducing the need to process the raw intervals from all_mbr_z_intervals.

            * NOTE: The in-memory tree structure (IntervalCracking instances) already captures the current state and is more efficient to use for queries.
        """
        
        xmin, ymin, xmax, ymax = query
        # Calculate the Z-interval of the range query
        zmin = MortonCode().interleave_latlng(ymin, xmin)
        zmax = MortonCode().interleave_latlng(ymax, xmax)
        queryZaddress = [zmin, zmax]

        # Step 1 - Filtering step to predict cluster IDs
        predicted_labels = self.predClusterIdsRangeQuery(model, queryZaddress)

        # Step 2 - Cracking the predicted clusters
        query_rect = Interval(zmin, zmax)
        query_results = []
        for cluster_id, _ in predicted_labels:
            # Check if the cluster has been indexed already
            if cluster_id not in CrackingSPLindex.cluster_indices:
                # Load the intervals for the cluster only once
                pred_cluster = all_mbr_z_intervals.get(cluster_id)
                if not pred_cluster:
                    continue       # Skip if no cluster found
                    
                 # Store the IntervalCracking instance for this cluster   
                CrackingSPLindex.cluster_indices[cluster_id] = IntervalCracking(pred_cluster)
            
            # Use the already initialized IntervalCracking for this cluster
            adaptive_index = CrackingSPLindex.cluster_indices[cluster_id]
            # Perform adaptive search and cracking
            query_result = adaptive_index.adaptiveSearch(query_rect, query)
            query_results.extend(query_result)
        return query_results



