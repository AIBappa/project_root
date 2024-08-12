from .models import Category, Place, City, Contact
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class PlaceSerializer(GeoFeatureModelSerializer):
    categories = serializers.SlugRelatedField(queryset=Category.objects.all(), slug_field='category_name')

    class Meta:
        model = Place
        geo_field = 'point_geom'

        fields = ('pk', 'categories', 'place_name', 'description', 'created_at', 'modified_at', 'image',)

class CitySerializer(GeoFeatureModelSerializer):
    proximity = serializers.SerializerMethodField('get_proximity')

    # Proximity does not exist in database model, it is being derived here. It is referred in function above.
    def get_proximity(self, obj):
        if obj.distance:
            return obj.distance.km
        return False
    
    class Meta:
        model = City
        geo_field = 'wkb_geometry'

        fields = (
            'ogc_fid',
            'oldname',
            'name',
            'wkb_geometry',
            'proximity',
        )

class ContactSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Contact
        geo_field = 'gps_location'
        fields = ['id', 'name', 'mobile', 'address', 'gps_location', 'email']

