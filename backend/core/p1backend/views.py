from .models import Place, Category, City, Contact
from .serializers import CategorySerializer, PlaceSerializer, CitySerializer, ContactSerializer
from rest_framework import generics,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import Http404
from django.contrib.gis.db.models.functions import Distance
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point

# Create your views here.
class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    name = 'category-list'

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    name = 'category-detail'

# Note that with the filter, whichever places that are clicked as Active (in checkbox in pgadmin) will be shown. So it is a tool to stop certain ads from being shown.
class PlaceList(generics.ListAPIView):
    queryset = Place.objects.filter(active=True)
    serializer_class = PlaceSerializer
    name = 'places-list'

class PlaceDetail(generics.RetrieveAPIView):
    queryset = Place.objects.filter(active=True)
    serializer_class = PlaceSerializer
    name = 'places-detail'

class CityList(generics.ListAPIView):
    serializer_class = CitySerializer
    name = 'cities-list'

    # queryset function is being overriden in this class
    def get_queryset(self):
        placeID = self.request.GET.get('placeid')

        if placeID is None:
            raise Http404("Place ID parameter is missing")
        
        try:     
            selectedPlace = get_object_or_404(Place, pk=placeID)
        except Place.DoesNotExist:
            raise Http404("Place not found")
        
        selectedPlaceGeom = selectedPlace.point_geom
        nearestCities = City.objects.annotate(distance=Distance('wkb_geometry', selectedPlaceGeom)).order_by('distance')[:4]
        return nearestCities
    
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    name = 'contact-list'
    
    # @action(detail=False, methods=['get'])
    # def nearby(self, request):
    #     try:
    #         lat = float(request.query_params.get('lat'))
    #         lng = float(request.query_params.get('lng'))
    #         proximity = float(request.query_params.get('proximity', 5))  # Default to 5 km if not provided

    #         user_location = Point(lng, lat, srid=4326)
    #         contacts = Contact.objects.annotate(
    #             distance=Distance('location', user_location)
    #         ).filter(distance__lte=proximity * 1000)  # Convert km to meters

    #         serializer = self.get_serializer(contacts, many=True)
    #         return Response(serializer.data)
    #     except (TypeError, ValueError):
    #         return Response({'error': 'Invalid parameters'}, status=400)
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        try:
            # Get latitude, longitude, and proximity from query parameters
            lat = float(request.query_params.get('lat'))
            lng = float(request.query_params.get('lng'))
            proximity = float(request.query_params.get('proximity', 5))  # Default to 5 km if not provided

            # Create a Point object for the user's location
            user_location = Point(lng, lat, srid=4326)

            # Filter contacts within the specified proximity
            contacts = Contact.objects.annotate(
                distance=Distance('gps_location', user_location)
            ).filter(distance__lte=proximity * 1000)  # Convert km to meters

            # Serialize and return the data
            serializer = self.get_serializer(contacts, many=True)
            return Response(serializer.data)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid parameters'}, status=400)


    