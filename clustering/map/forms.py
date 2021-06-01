from django import forms
from map.models import Point


class PointFormCoord(forms.ModelForm):
    """
    Form class if the user wants to define a point with (latitude, longitude) coordinates
    """
    class Meta:
        model = Point
        fields = ('state', 'latitude', 'longitude', 'date')
        
        widgets = {}
        

class PointFormAddr(forms.ModelForm):
    """
    Form class if the user wants to define a point with an address
    """
    class Meta:
        model = Point
        fields = ('state', 'address', 'date')
        
        widgets = {}
        

class GeneratePointsForm(forms.ModelForm):
    """
    Form class to generate random points for a given date,
    using the known data
    """
    class Meta:
        model = Point
        fields = ('date',)
        
        widgets = {}