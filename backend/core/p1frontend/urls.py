from django.urls import path
from . import views

app_name = 'p1frontend'
urlpatterns = [
    path('', views.placesListMap, name='placeslist_map'),
]