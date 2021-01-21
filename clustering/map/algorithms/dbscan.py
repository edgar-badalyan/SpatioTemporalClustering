import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import haversine_distances

class DBSCAN_Clustering:
    """
    Computes clusters for given points with DBSCAN algorithm
    """
    points = []
    
    def __init__(self, point_data):
        self.points = point_data
        
    def transform_data(self):
        """
        Put points in Numpy array with correct data type for convenience
        """
        
        X = np.asarray([[float(p.latitude), float(p.longitude)] for p in self.points])
        
        return X
        
    def compute_clusters(self):
        """
        Find clusters
        """
        X = self.transform_data()
        
        X_rad = np.array([np.radians(i) for i in X]) #scikit method takes radians
        
        distance_pairs = haversine_distances(X_rad, X_rad) # 2-D table of haversine distances between each pair of points

        distance_pairs *= 6378137 # multiply by radius of Earth
        
        # epsilon is the max distance for 2 points to be considered "close"
        # in this case, 250 meters. It has been chosen by experimentation.
        Y = DBSCAN(eps=250, metric="precomputed").fit_predict(distance_pairs)
        centroids = np.asarray([np.mean(X[Y==i], axis=0) for i in range(np.max(Y)+1)])

        return Y, centroids

   