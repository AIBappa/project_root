from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'contacts', views.ContactViewSet, basename='contact')

# URL patterns
urlpatterns = [
    path('categories/', views.CategoryList.as_view(), name=views.CategoryList.name),
    path('categories/<int:pk>/', views.CategoryDetail.as_view(), name=views.CategoryDetail.name),
    path('places/', views.PlaceList.as_view(), name=views.PlaceList.name),
    path('places/<int:pk>', views.PlaceDetail.as_view(), name=views.PlaceDetail.name),
    path('cities/', views.CityList.as_view(), name=views.CityList.name),
    path('', include(router.urls)),
    #path('kosnoztik/', viewsbackup.hello_world, name='hello_world'),
    #path('places/', viewsbackup.all_places, name = 'all_places'),
    #path('places/<int:rk>/', viewsbackup.place_detail, name = 'place_single_detail'),
]