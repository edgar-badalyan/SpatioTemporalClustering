import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import haversine_distances


class DBSCANClustering:
    """
    Computes clusters for given points with DBSCAN algorithm
    """
    points = []
    
    def __init__(self, point_data):
        """
        Constructor

        Parameters
        ----------
            point_data : QuerySet
                points to be clustered
        """
        self.points = point_data

    def distance_between_dates(self, p, p2):
        """
        Compute date distance between two points, i.e. the absolute value
        of the difference in days, normalized.

        Parameters
        ----------
            p : Point
                first point
            p2 : Point
                second point
        Returns
        -------
            delta : float
                time distance
        """
        delta = abs(p.date - p2.date)
        return delta.days/10

    def transform_data(self):
        """
        Put points in Numpy array with correct data type for convenience.
        Also compute date distance matrix.

        Returns
        -------
            X : numpy array
                coordinates of the points
            date_distances : numpy array
                time distance matrix
        """
        X = np.asarray([[float(p.latitude), float(p.longitude)] for p in self.points])

        num_points = len(self.points)
        date_distances = np.zeros((num_points, num_points))

        for i, p in enumerate(self.points):
            for j, p2 in enumerate(self.points):
                date_distances[i, j] = self.distance_between_dates(p, p2)

        return X, date_distances
        
    def compute_clusters(self):
        """
        Find clusters using DBSCAN algorithm

        Returns
        -------
            tup : tuple
                centroids, sizes, and number of points of cluster found
        """
        X, date_distances = self.transform_data()

        X_rad = np.array([np.radians(i) for i in X])  # scikit method takes radians

        # 2-D table of haversine distances between each pair of points
        distance_pairs = haversine_distances(X_rad, X_rad)

        distance_pairs /= distance_pairs.max()  # Normalize distances

        # Weight of space and time distances
        # Found by experimentation
        prop = 0.98

        # Distance is weighted average of space distance and time distance
        space_time_distance = prop*distance_pairs + (1-prop)*date_distances

        # epsilon is the max distance for 2 points to be considered "close"
        # 0.014 has been found by experimentation
        Y = DBSCAN(eps=0.014, metric="precomputed").fit_predict(space_time_distance)

        return self.get_cluster_data(X, Y)

    def get_cluster_data(self, X, Y):
        """
        Use clustering computed by DBSCAN to find:
        * centroid of each cluster
        * number of points per cluster
        * radius of each cluster

        Parameters
        ----------
            X : numpy array
                points clustered
            Y : numpy array
                cluster decision vector
        Returns
        -------
            centroids : list
                centroids of clusters
            sizes : list
                sizes of clusters (in kilometers)
            num_points : list
                number of points in clusters
        """

        centroids = []
        num_points = []
        sizes = []

        for i in range(np.max(Y) + 1):
            points_in_cluster = X[Y == i]

            # Centroid is arithmetic mean of point coordinates
            centroid = np.mean(points_in_cluster, axis=0)
            centroids.append(centroid)

            num_points.append(len(points_in_cluster))

            # Radius of cluster is distance from centroid to farthest point
            size = 0
            for point in points_in_cluster:
                point = np.array([np.radians(i) for i in point])
                centroid_rad = np.array([np.radians(i) for i in centroid])
                distance = haversine_distances([point], [centroid_rad])[0][0]
                if distance > size:
                    size = distance

            # Multiply by radius of Earth to get kilometers
            size *= 6371
            sizes.append(size)

        return centroids, num_points, sizes
