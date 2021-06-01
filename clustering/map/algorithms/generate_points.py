import pandas as pd
import numpy as np
import os


class PointGenerator():
    """
    Class used to generate random points on a given day.
    """

    def __init__(self, past_points, date):
        """
        Constructor

        Parameters
        ----------
            past_points : QuerySet
                points from the past 10 days
            date : str
                date for which to generate
        """
        self.past_points = past_points
        self.date = date
        self.R = 6371000
    
    def generate(self):
        """
        Read number of points to generate and data on municipalities.
        Then, for each municipality, generate given number of points

        Returns
        -------
            all_points : list
            generated points
        """

        # File with number of cases per day and per municipality
        wd = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(wd, "../data/data_municipality.csv")
        df = pd.read_csv(file_path, sep=";")

        # Data on municipality shapes
        circle_path = os.path.join(wd, "../data/circles.csv")
        self.circles_data = pd.read_csv(circle_path, sep=";")
        
        values = df[df["DATE"] == str(self.date)]
        
        
        self.to_generate_dict = {}
        
        for mun, cases in zip(values["TX_DESCR_FR"], values["CASES"]):
            if cases == "<5":
                self.to_generate_dict[mun] = 3
            else:
                self.to_generate_dict[mun] = int(cases)
                
                
        print(self.to_generate_dict)

        # Generated points
        all_points = []
        
        for mun in self.to_generate_dict.keys():
            mun_points = self.past_points.filter(municipality__iexact=mun)
            new_points = self.random_points(mun, mun_points)
            all_points += new_points
        
        return all_points
        
    
    def random_points(self, mun, mun_points):
        """
        Generate new points. If there are enough points in past history,
        generate with normal distribution and center around centroid of past points.
        Otherwise, generate with uniform distribution and center around municipality center.

        Parameters
        ----------
            mun : str
                municipality name
            mun_points : QuerySet
                past points of the municipality

        Returns
        -------
            new_points : list
                new points in the municipality
        """
        new_points = []
        mun_row = self.circles_data.loc[self.circles_data["municipality"] == mun]

        # Read municipality data
        mun_center = mun_row["center"].iloc[0][1:-1]
        mun_center = mun_center.split(',')
        mun_radius = mun_row["radius"].iloc[0]
        
        mun_center = [float(coord) for coord in mun_center]
        mun_radius = float(mun_radius)

        number_points = self.to_generate_dict[mun]

        if len(mun_points) < 20:
            print(mun, "uniform")
            angles, radii = self.generate_uniform(number_points, mun_radius)
            center = mun_center
        else:
            print(mun, "normal")
            angles, radii, center = self.generate_normal(number_points, mun_radius, mun_points)

        for angle, radius in zip(angles, radii):
            p = self.circle_point(center[0], center[1], radius/self.R, angle)
            new_points.append([self.cartesian_to_latlng(p), mun])
            
        return new_points
    
    def generate_uniform(self, number_points, mun_radius):
        """
        Generate distances and angles for the new points.
        Distances are taken from uniform distribution [0, mun_radius],
        and angles from uniform distribution [0, 360]

         Parameters
        ----------
            number_points : int
                number of points to generate
            mun_radius : float
                radius of the municipality

        Returns
        -------
            angles : numpy array
                angles of the points
            radii : numpy array
                radii of the new points
        """
        angles = 360*np.random.uniform(low=0, high=1, size=number_points)
        radii = mun_radius*np.random.uniform(low=0, high=1, size=number_points)
        
        return angles, radii


    def generate_normal(self, number_points, mun_radius, mun_points):
        """
        Generate distances and angles for the new points.
        Distances are taken from normal distribution N(0, mun_radius/2),
        and angles from uniform distribution [0, 180].
        Also compute and return centroid of past points

        Parameters
        ----------
            number_points : int
                number of points to generate
            mun_radius : float
                radius of the municipality
            mun_points : QuerySet
                past points of the municipality

        Returns
        -------
            angles : numpy array
                angles of the points
            radii : numpy array
                radii of the new points
            centroid : list
                coordinates of the centroid of past points
        """
        centroid = [0, 0]
        
        for p in mun_points:
            centroid[0] += float(p.latitude)
            centroid[1] += float(p.longitude)
            
        centroid[0] /= len(mun_points)
        centroid[1] /= len(mun_points)
        
        angles = 180*np.random.uniform(low=0, high=1, size=number_points)
        radii = np.random.normal(loc=0, scale=mun_radius/2, size=number_points)
        
        return angles, radii, centroid
    
    
    def latlng_to_cartesian(self, lat, lng):
        """
        Convert from latitude/longitude system to cartesian

        Parameters
        ----------
            lat : float
                latitude of the point
            lng : float
                longitude of the point

        Returns
        -------
            P : numpy array
                cartesian coordinates of the point
        """
        lat_rad = np.radians(lat)
        lng_rad = np.radians(lng)
    
        X = self.R * np.cos(lat_rad) * np.cos(lng_rad)
        Y = self.R * np.cos(lat_rad) * np.sin(lng_rad)
        Z = self.R * np.sin(lat_rad)
        
        return np.array([X, Y, Z])
    
    def cartesian_to_latlng(self, P):
        """
        Convert from cartesian system to latitude/longitude

        Parameters
        ----------
            P : numpy array
                cartesian coordinates of the point

        Returns
        -------
            lat : float
                latitude of the point
            lng : float
                longitude of the point
        """
        X, Y, Z = P[0], P[1], P[2]
        
        lat = np.arcsin(Z/self.R)
        lng = np.arctan2(Y, X)
        
        return np.rad2deg(lat), np.rad2deg(lng)
    
    def reverse_haversine(self, P, D):
        """
        Given point P, find one of the 2 points that have haversine distance
        of D from P, and that have the same latitude as P

        Parameters
        ----------
            P : numpy array
                cartesian coordinates of the original point
            D : float
                distance at which the new point must lie

        Returns
        -------
            lat : float
                latitude of the new point
            lng : float
                longitude of the new point
        """
        p_rad = np.array([np.radians(i) for i in P])
        latP, lngP = p_rad[0], p_rad[1]
        latQ = latP
    
        frac = (np.sin(D/2)**2)/(np.cos(latP)**2)
        lngQ = lngP - 2*np.arcsin(np.sqrt(frac))
        return np.rad2deg(latQ), np.rad2deg(lngQ)

    def vectors(self, P, Q):
        """
        Given original point P, and point Q on the circle around P, find
        two orthogonal vectors of the plane that contains the circle.

        Parameters
        ----------
            P : numpy array
                cartesian coordinates of the original point
            Q: numpy array
                cartesian coordinates of the point on the circle
        Returns
        -------
            u : numpy array
                3D vector that is on the plane
            v : numpy array
                3D vector that is on the plane, orthogonal to u
        """
        Xp, Yp, Zp = P[0], P[1], P[2]
        Xq, Yq, Zq = Q[0], Q[1], Q[2]
        dot_prod = Xp*Xq + Yp*Yq + Zp*Zq
        Zr = (dot_prod - Xp - Yp)/Zp
        
        R = np.array([1, 1, Zr])
        
        u = Q - R
        v = np.cross(P, u)
        
        u /= np.linalg.norm(u)
        v /= np.linalg.norm(v)
        
        return u, v
    
    def circle_point(self, latP, longP, r, t):
        """
        Given original point P, a distance r, and an angle t, find
        the new point.

        Parameters
        ----------
            latP : float
                latitude of the original point
            longP : float
                longitude of the original point
            r: float
                distance of the new point to the original point
            t: float
                angle of the new point relative to the original point
        Returns
        -------
            S : numpy array
                cartesian coordinates of the new point
        """
        latQ, longQ = self.reverse_haversine([latP,  longP], r) 
        
        P = self.latlng_to_cartesian(latP, longP)
        Q = self.latlng_to_cartesian(latQ, longQ)

        Xp, Yp, Zp = P[0], P[1], P[2]
        Xq, Yq, Zq = Q[0], Q[1], Q[2]
        
        u, v = self.vectors(P, Q)
        
        squared_sum = Xp**2 + Yp**2 + Zp**2
        dot_prod = Xp*Xq + Yp*Yq + Zp*Zq
        C = (dot_prod/squared_sum) * P
        S = C + r * self.R * np.cos(t)*u + r * self.R * np.sin(t)*v
        return S