import pandas as pd
import numpy as np
import os

class PointGenerator():
    def __init__(self, past_points, date):
        self.past_points = past_points
        self.date = date
        self.R = 6371000
    
    def generate(self):
        
                
        wd = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(wd, "../data/brussels_data.csv")
        df = pd.read_csv(file_path, sep=";")
        
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
        
        all_points =[]
        
        for mun in self.to_generate_dict.keys():
            mun_points = self.past_points.filter(municipality__iexact=mun)
            new_points = self.random_points(mun, mun_points)
            all_points += new_points
        
        return all_points
        
    
    def random_points(self, mun, mun_points):
        new_points = []
        mun_row = self.circles_data.loc[self.circles_data["municipality"]==mun]
        
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
        
        angles = 360*np.random.uniform(low=0, high=1, size=number_points)
        radii = mun_radius*np.random.uniform(low=0, high=1, size=number_points)
        
        return angles, radii
        
    
    def generate_normal(self, number_points, mun_radius, mun_points):
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

        lat_rad = np.radians(lat)
        lng_rad = np.radians(lng)
    
        X = self.R * np.cos(lat_rad) * np.cos(lng_rad)
        Y = self.R * np.cos(lat_rad) * np.sin(lng_rad)
        Z = self.R * np.sin(lat_rad)
        
        return np.array([X, Y, Z])
    
    def cartesian_to_latlng(self, P):
        X, Y, Z = P[0], P[1], P[2]
        
        lat = np.arcsin(Z/self.R)
        lng = np.arctan2(Y, X)
        
        return np.rad2deg(lat), np.rad2deg(lng)
    
    def reverse_haversine(self, P, D):
        p_rad = np.array([np.radians(i) for i in P])
        latP, lngP = p_rad[0], p_rad[1]
        latQ = latP
    
        frac = (np.sin(D/2)**2)/(np.cos(latP)**2)
        lngQ = lngP - 2*np.arcsin(np.sqrt(frac))
        return np.rad2deg(latQ), np.rad2deg(lngQ)

    def vectors(self, P, Q):
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