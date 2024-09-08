import os
import sys
sys.path.append("../")


class Config(object):
    """Configuration class."""

    class __Singleton(object):
        """Singleton design pattern."""

        def __init__(self):
            # params for clustering algorithm
            self.bf = 10
            self.n_clusters = None
            self.threshold = 11.5
            self.max_depth = 300

            # Data path
            filename = "data/"
            self.water_query_range_path = os.path.join(filename, "water_query_ranges_1%.npy")
            self.lakes_query_range_path = os.path.join(filename, "lakes_query_ranges_100K.npy")
            self.roads_query_range_path = os.path.join(filename, "roads_query_ranges_100K.npy")
            self.uniform_polygon_name = filename + "data/SynPolyUniform_5M.npy"  # PolyUniform data path
            self.lakes_polygon_name = filename + "data/LandPolygons.npy"  # LandPolygon data path
            self.water_polygon_name = filename + "data/water_poly.npy"  # WaterPolygon data path
            self.roads_polygon_name = filename + "data/PolyCorrelated5M.npy"  # PolyCorrelated data path

            print('---------Config is initilized----------')
    instance = None

    def __new__(cls):
        """Return singleton instance."""
        if not Config.instance:
            Config.instance = Config.__Singleton()
        return Config.instance

    def __getattr__(self, name):
        """Get singleton instance's attribute."""
        return getattr(self.instance, name)

    def __setattr__(self, name):
        """Set singleton instance's attribute."""
        return setattr(self.instance, name)
