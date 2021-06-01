from django.shortcuts import redirect
from django.views.generic import TemplateView, CreateView
from map.models import Point
from map.forms import PointFormCoord, PointFormAddr, GeneratePointsForm
from map.algorithms.dbscan import DBSCANClustering
import geopy as gp
from random import randint
import datetime
from map.algorithms.generate_points import PointGenerator
from geopy.extra.rate_limiter import RateLimiter
import csv
from django.http import HttpResponse


class AboutView(TemplateView):
    """
    Presents the project
    """
    template_name = 'map/about.html'


class MapView(TemplateView):
    """ 
    Show the map. Mother class for PointView and ClusterView
    """

    # Base template that will be inherited
    template_name = 'map/map_base.html'
    context_object_name = "data_dict"

    default_date = datetime.date(year=2021, month=1, day=1)  # default day is January first

    def get_queryset(self, request_date=None):
        """ 
        Get data from database. 
        If request_date is specified, return only points of past 10 days
        """
        if request_date is None:
            return Point.objects.all()
        else:
            return Point.objects.filter(date__gte=request_date - datetime.timedelta(days=10),
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


class PointView(MapView):
    """
    Display with all points
    """

    template_name = 'map/map_points.html'

    def format_point_data(self, points):
        """
        Put data points in a dict with GEOJSON syntax, to simplify display later
        """
        point_data_dict = {"type": "FeatureCollection",
                           "features": []}

        for point in points:

            point_dict = {"type": "Feature",
                          "properties": {"state": str(point.state),
                                         "date": str(point.date)},

                          "geometry": {"type": "Point",
                                       "coordinates": [str(point.longitude), str(point.latitude)]}
                          }

            point_data_dict["features"].append(point_dict)

        return point_data_dict

    def get_context_data(self, **kwargs):
        """
        Send data to template_name
        """

        data_dict = super(MapView, self).get_context_data(**kwargs)

        request_date = self.get_date(**kwargs)

        points = self.get_queryset(request_date)

        point_data_dict = self.format_point_data(points)

        data_dict["date"] = {"day": request_date.day, "month": request_date.month, "year": request_date.year}
        data_dict["mode"] = "point"
        data_dict["point_data"] = point_data_dict

        return data_dict


class ClusterView(MapView):
    """ 
    Display points with cluster colors, and centroids
    """

    template_name = 'map/map_clusters.html'

    def format_centroids(self, centroids, num_points, sizes):
        """
        Format centroid data in GEOJSON syntax
        """
        centroid_data_dict = {"type": "FeatureCollection",
                              "features": []}

        for centroid, num, size in zip(centroids, num_points, sizes):
            centroid_dict = {"type": "Feature",

                             "geometry": {"type": "Point",
                                          "coordinates": [str(centroid[1]), str(centroid[0])]},
                             "properties": {"size": str(size),
                                            "numPoints": str(num)},
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

        if len(points) == 0:  # Can't cluster if there are no points
            point_clusters, centroids = [], []
            num_points, sizes = [], []
        else:

            DBSCAN = DBSCANClustering(points)

            centroids, num_points, sizes = DBSCAN.compute_clusters()

            print(centroids)
            print(num_points)
            print(sizes)

        data_dict["date"] = {"day": request_date.day, "month": request_date.month, "year": request_date.year}
        data_dict["mode"] = "cluster"
        data_dict["centroids"] = self.format_centroids(centroids, num_points, sizes)

        return data_dict


class PointCoordCreateView(CreateView):
    """ 
    Create a new point in the dataset, with given coordinates
    """
    template_name = 'map/point_form_coord.html'
    redirect_field_name = 'map/map_clusters.html'
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

        address = geolocator.reverse(str(lat) + ", " + str(lng))
        self.object.address = address.address
        raw_dict = address.raw

        # Try to find the name of the municipality in the address
        possible_names = ["town", "village", "municipality"]
        for name in possible_names:
            if name in raw_dict["address"]:
                self.object.municipality = raw_dict["address"][name]
                break
        else:
            self.object.municipality = "Unknown"

        self.object.save()

        return redirect('map_clusters')


class PointAddrCreateView(CreateView):
    """ 
    Create a new point in the dataset, with given coordinates
    """
    template_name = 'map/point_form_addr.html'
    redirect_field_name = 'map/map_clusters.html'
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

        return redirect('map_clusters')


class GeneratePointView(TemplateView):
    """
    Class used to automatically generate points
    """
    template_name = 'map/generate_point.html'
    redirect_field_name = 'map/map_clusters.html'
    model = Point


def generate_points(request):
    """
    Use the PointGenerator to generate points on a given day,
    using available data
    """
    if request.method == "POST":

        # Get date
        date_str = request.POST.get('date')

        date_lst = date_str.split("-")
        date = datetime.date(year=int(date_lst[0]), month=int(date_lst[1]), day=int(date_lst[2]))
        print(date)

        # Get points of the past 10 days
        past_points = Point.objects.filter(date__gte=date - datetime.timedelta(days=10),
                                           date__lte=date)

        # Generate points
        pg = PointGenerator(past_points, date)
        new_points = pg.generate()

        # Add points to database
        for point in new_points:
            lat = point[0][0]
            lng = point[0][1]
            municipality = point[1]

            geolocator = gp.Nominatim(user_agent='CovidClusteringLocator')

            # Use a rate limiter so as not to overflow the geocoding server
            reverse_geocoder = RateLimiter(geolocator.reverse, min_delay_seconds=1)

            address = reverse_geocoder(str(lat) + ", " + str(lng)).address

            p = Point.objects.create_point(1, lat, lng, address, municipality, date)
            p.save()

    return redirect('generateView')
