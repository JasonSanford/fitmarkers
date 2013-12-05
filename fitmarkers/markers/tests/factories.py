import datetime
import json
import random

from django.contrib.gis.geos import GEOSGeometry
import factory

from fitmarkers.markers.models import Marker

class MarkerFactory(factory.Factory):
    FACTORY_FOR = Marker

    geom = factory.LazyAttribute(lambda o: generate_geom())
    

def random_coordinate():
    x_coordinate_range = (-105, -95)
    y_coordinate_range = (35, 45)
    return (random.randint(*x_coordinate_range), random.randint(*y_coordinate_range))

def generate_geom():
    point = {'type': 'Point', 'coordinates': random_coordinate()}
    geom = GEOSGeometry(json.dumps(point))
    return geom