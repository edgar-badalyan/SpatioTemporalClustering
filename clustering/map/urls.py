# -*- coding: utf-8 -*-
"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from map import views

urlpatterns = [
    path('about/', views.AboutView.as_view(), name='about'),   
    
    # see the data on default day
    path('', views.PointView.as_view(), name='map'),
    path('clusters', views.ClusterView.as_view(), name='map_cluster'),
    
    # see the data on given day
    path('date/<str:date>', views.PointView.as_view(), name='map_date'),   
    path('clusters/date/<str:date>', views.ClusterView.as_view(), name='map_date_cluster'), 
    
    # add a new point
    path('new_coord/', views.PointCoordCreateView.as_view(), name='new_point_coord'),
    path('new_addr/', views.PointAddrCreateView.as_view(), name='new_point_addr'),
    
    # generate random points
    path('generate_points/', views.add_random_points, name='generate_points'),
]