from django.db import models
from django.contrib.gis.db import models

# Create your models here.
class Category(models.Model):
    category_name = models.CharField('Category Name', max_length=50, help_text='Specified Name')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.category_name
    
class Place(models.Model):
    categories = models.ForeignKey(Category, on_delete=models.CASCADE)
    place_name = models.CharField(max_length=50)
    description = models.CharField(max_length=254, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='place_images/', blank=True, null=True)
    active = models.BooleanField(default=True)
    point_geom = models.PointField()

    class Meta:
        verbose_name_plural = 'Places'

    def __str__(self):
        return self.place_name
    
class City(models.Model):
    ogc_fid = models.AutoField(primary_key=True)
    # ogc_fid = models.IntegerField(primary_key=True, default=1)
    oldname = models.CharField(max_length=100)  # Assuming id contains alphanumeric names
    name = models.CharField(max_length=100)
    wkb_geometry = models.GeometryField()

    class Meta:
        db_table = "Cities_India"
        verbose_name_plural = 'Cities'

    def __str__(self):
        return self.name
    
class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    gps_location = models.PointField()
    email = models.CharField(max_length=100)
    
    class Meta:
        db_table = "cosellwkt"
        managed = False

    def __str__(self):
        return self.name


