"""
URL configuration for safepath project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, re_path as url
from explorer import views

urlpatterns = [
    url(r'^/', views.index, name="index"),
    url(r'^signin/', views.signin, name="signin"),
    url(r'^logout/', views.logout, name="logout"),
    url(r'^signup/', views.signup, name="signup"),
    url(r'^verify/', views.verify, name="verify"),
    url(r'^home/', views.home, name='home'),
    url(r'^travel/', views.travel, name='travel'),
    url(r'^travel_map/', views.travel_map, name='travel_map'),
]
