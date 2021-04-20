from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView
from map.models import Point
from map.forms import PointFormCoord, PointFormAddr, GeneratePointsForm
from map.algorithms.dbscan import DBSCAN_Clustering
import geopy as gp
from random import randint
import datetime
from map.algorithms.generate_points import PointGenerator
from geopy.extra.rate_limiter import RateLimiter
# Create your views here.

class AboutView(TemplateView):
    """
    Presents the project
    """
    template_name = 'map/about.html'
    
    
    
class MapView(TemplateView):
    """ 
    See the map with the points. Mother class for PointView and ClusterView
    """
    
    template_name = 'map/map.html'
    context_object_name = "data_dict"
    
    default_date = datetime.date(year=2020, month=12, day=27) # default day is 27th of december
         
        
    def get_queryset(self, request_date=None):
        """ 
        Get data from database. 
        If request_date is specified, only show points for that day
        """
        if request_date is None:
            return Point.objects.all()
        else: 
            return Point.objects.filter(date__gte=request_date,
                                        date__lte=request_date)
       
    def get_date(self, **kwargs):
        """ 
        Read given date string and convert to Python date format
        """
        if 'date' in kwargs: 
       
            date_string = kwargs["date"].split("-")
            
            # Warning: Python and JS don't put dates is same order:
            # Pay attention to indexes 
            return datetime.date(day=int(date_string[1]), 
                                month=int(date_string[0]), 
                                year=int(date_string[2]))
        else:
            return self.default_date
            
    
    def format_point_data(self, points, request_date, clusters):
        """
        Put data points in a dict with GEOJSON syntax, to simplify display later
        """
        point_data_dict = {"type": "FeatureCollection",
                           "features": []}

        i = 0
        for point in points:
        
            if clusters is None: # With point mode
                cluster_id = -1 
            else:                # With cluster mode
                cluster_id = clusters[i]
                i+=1
                
            point_dict = {"type": "Feature",
                          "properties": {"state": str(point.state),
                                         "date": str(point.date),
                                         "cluster": str(cluster_id)},
                                         
                          "geometry": { "type": "Point",
                                        "coordinates": [str(point.longitude),  str(point.latitude)]}
                         }
                          
            point_data_dict["features"].append(point_dict)
            
        return point_data_dict
            
            
 
 
class PointView(MapView):
    """
    Display with all points
    """
    
    def get_context_data(self, **kwargs):
        """
        Send data to template_name
        """
        
        data_dict = super(MapView, self).get_context_data(**kwargs)
        
        request_date = self.get_date(**kwargs)
        
        points = self.get_queryset(request_date)
        
        point_data_dict = self.format_point_data(points, request_date, clusters=None)
                
        data_dict["date"] = {"day" : request_date.day, "month": request_date.month, "year":request_date.year}
        data_dict["mode"] = "point"
        data_dict["point_data"] = point_data_dict
        
        
        return data_dict

class ClusterView(MapView):
    """ 
    Display points with cluster colors, and centroids
    """

    def format_centroids(self, centroids):
        """
        Format centroid data in GEOJSON syntax
        """
        centroid_data_dict = {"type": "FeatureCollection",
                           "features": []}
                           
        for centroid in centroids:
            centroid_dict = {"type": "Feature",
            
                              "geometry": { "type": "Point",
                                            "coordinates": [str(centroid[1]),  str(centroid[0])]}
                             }
                          
            centroid_data_dict["features"].append(centroid_dict)
            
            
        return centroid_data_dict
        
        
    
    def get_context_data(self, **kwargs):
        """
        Send data to template_name
        """
        data_dict = super(MapView, self).get_context_data(**kwargs)
        
        request_date = self.get_date(**kwargs)
  
        
        points = self.get_queryset(request_date)

        DBSCAN = DBSCAN_Clustering(points)
        
        point_clusters, centroids = DBSCAN.compute_clusters() 
        
        point_data_dict = self.format_point_data(points, request_date, clusters=point_clusters)
                
        
        data_dict["date"] = {"day" : request_date.day, "month": request_date.month, "year":request_date.year}   
        data_dict["mode"] = "cluster"
        data_dict["point_data"] = point_data_dict
        data_dict["centroids"] = self.format_centroids(centroids)
        
        return data_dict
    
        
        
 
class PointCoordCreateView(CreateView):
    """ 
    Create a new point in the dataset, with given coordinates
    """
    template_name = 'map/point_form_coord.html'
    redirect_field_name = 'map/map.html'   
    form_class = PointFormCoord 
    model = Point
    
    def form_valid(self, form):
        """
        Verify form and save object
        """
        self.object = form.save(commit=False)
        
        lat = self.object.latitude
        lng = self.object.longitude
        
        # Use Geocoding to find address
        geolocator = gp.Nominatim(user_agent='CovidClusteringLocator')
        self.object.address = geolocator.reverse(str(lat) + ", " + str(lng)).address
        
        raw_dict = geolocator.reverse(str(lat) + ", " + str(lng)).raw
        self.object.municipality = raw_dict["address"]["town"]
        
        self.object.save()

        return redirect('map')
    

class PointAddrCreateView(CreateView):
    """ 
    Create a new point in the dataset, with given coordinates
    """
    template_name = 'map/point_form_addr.html'
    redirect_field_name = 'map/map.html'   
    form_class = PointFormAddr 
    model = Point
    
    def form_valid(self, form):
        """
        Verify form and save object
        """
        self.object = form.save(commit=False)
        
        addr = self.object.address
        
        
        # Use Geocoding to find coordinates
        geolocator = gp.Nominatim(user_agent='CovidClusteringLocator')
        
        coords = geolocator.geocode(addr)
        self.object.latitude = coords.latitude
        self.object.longitude = coords.longitude
        
        raw_dict = geolocator.reverse(str(coords.latitude) + ", " + str(coords.longitude)).raw
        self.object.municipality = raw_dict["address"]["town"]
        
        self.object.save()

        return redirect('map')
        

class GeneratePointView(TemplateView):
    template_name = 'map/generate_point.html'
    redirect_field_name = 'map/map.html'   
    model = Point
    
        


def generate_points(request):
    if request.method == "POST":
        
        date_str = request.POST.get('date')
        
        date_lst = date_str.split("-")
        date = datetime.date(year=int(date_lst[0]), month=int(date_lst[1]), day=int(date_lst[2]))
        print(date)
        
        past_points = Point.objects.filter(date__gte=date - datetime.timedelta(days=14),
                                        date__lte=date)

        pg = PointGenerator(past_points, date)
        new_points = pg.generate()
       
        for point in new_points:
            lat = point[0][0]
            lng = point[0][1]
            municipality = point[1]
            
            geolocator = gp.Nominatim(user_agent='CovidClusteringLocator')
            
            reverse_geocoder = RateLimiter(geolocator.reverse, min_delay_seconds=1)
            
            address = reverse_geocoder(str(lat) + ", " + str(lng)).address
            
            p = Point.objects.create_point(1, lat, lng, address, municipality, date)
            p.save()
            
    return redirect('generateView')
    

def add_random_points(request):
    """
    Generate random points and add to dataset
    """
    if request.method == "POST":
      
        new_points = generate_random_points(((50.82283, 4.35791), (50.80956, 4.40175)), 100)
        
        for point in new_points:
            lat = point[0]
            lng = point[1]
            geolocator = gp.Nominatim(user_agent='CovidClusteringLocator')
            address = geolocator.reverse(str(lat) + ", " + str(lng)).address

            p = Point.objects.create_point(1, lat, lng, address, datetime.date(year=2020, month=12, day=30))
            p.save()
            
    return redirect('map')
            
        
        
def generate_random_points(corner_coord, n_points):
    """
    Generate random points and add to dataset
    """
    random_points = []

    lat1 = int(min(corner_coord[0][0], corner_coord[1][0]) *100000)
    lng1 = int(min(corner_coord[0][1], corner_coord[1][1]) *100000)
    
    
    lat2 = int(max(corner_coord[0][0], corner_coord[1][0]) *100000)
    lng2 = int(max(corner_coord[0][1], corner_coord[1][1]) *100000)
    
    
    for i in range(n_points):
        rand_lat = randint(lat1, lat2)/100000
        rand_lng = randint(lng1, lng2)/100000
        random_points.append((rand_lat, rand_lng))
        
    return random_points
    
    

