from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def placesListMap(request):
    response = render(request, 'p1frontend/places_base.html') # Base response without cache control
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate' # Cache control options start from here till end.
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

