import logging
import numpy as np
from sklearn.cluster import Birch

from IntervalCracking import AdaptiveSPLindex, Interval
#from improvedIntervalCracking import AdaptiveSPLindex, Interval
from ConfigParam import Config
from ZAdress import MortonCode
from helpers import calculate_bounding_box

logging.basicConfig(level=logging.DEBUG)


class SPLindex:
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
        xmin, ymin, xmax, ymax = query
        zmin = MortonCode().interleave_latlng(ymin, xmin)
        zmax = MortonCode().interleave_latlng(ymax, xmax)
        queryZaddress = [zmin, zmax]

        # Step 1 - Filtering step to predict cluster IDs
        predicted_labels = self.predClusterIdsRangeQuery(model, queryZaddress)

        # Step 2 - Cracking the predicted clusters
        query_rect = Interval(zmin, zmax)
        query_results = []
        for cluster_id, _ in predicted_labels:
            if cluster_id not in SPLindex.cluster_indices:
                # Load the intervals for the cluster only once
                pred_cluster = all_mbr_z_intervals.get(cluster_id)
                if not pred_cluster:
                    continue
                SPLindex.cluster_indices[cluster_id] = AdaptiveSPLindex(pred_cluster)

            adaptive_index = SPLindex.cluster_indices[cluster_id]
            query_result = adaptive_index.adaptiveSearch(query_rect, query)
            query_results.extend(query_result)
        return query_results



