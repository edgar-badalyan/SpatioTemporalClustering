from django.db import models
from django.urls import reverse
from datetime import date

# Create your models here.


class PointManager(models.Manager):
    def create_point(self, state, lat, lng, address, date=None):
        if(date==None):
            return self.create(state=state, latitude=lat, longitude=lng, address=address)
        else:
            return self.create(state=state, latitude=lat, longitude=lng, address=address, date=date)
 


class Point(models.Model):
    """
    Class to represent a point (i.e. a registered case) in the data
    """
    objects = PointManager()
    
    NEGATIVE  = 0
    POSITIVE  = 1
    RECOVERED = 2
    UNKNOWN   = 3
    
    STATE_CHOICES = [(POSITIVE, "Positive"),
                     (NEGATIVE, "Negative"),
                     (RECOVERED, "Recovered"),
                     (UNKNOWN, "Unknown")]


    state = models.IntegerField(choices=STATE_CHOICES, default=POSITIVE)
    latitude = models.DecimalField(max_digits=7, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    
    address = models.CharField(max_length=512)
    
    date = models.DateField(default=date.today)
    
    
    
    def get_absolute_url(self):
        return reverse('map')
        
        
   
    