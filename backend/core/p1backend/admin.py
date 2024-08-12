from django.contrib.gis import admin
from .models import Category, Place, City

# Register your models here.
admin.site.register(Category)

class CustomGeoAdmin(admin.GISModelAdmin):
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom' : 11,
            'default_lon' : 133.74,
            'default_lat' : -24.06,
        }
    }

@admin.register(Place)
class PlaceAdmin(CustomGeoAdmin):
    pass

@admin.register(City)
class PlaceAdmin(CustomGeoAdmin):
    pass
