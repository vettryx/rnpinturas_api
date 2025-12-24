# apps/cities/urls.py

from django.urls import path
from .views import city_autocomplete_view

app_name = 'cities'

urlpatterns = [
    path("cities/api/autocomplete/", city_autocomplete_view, name="city-autocomplet"),
]