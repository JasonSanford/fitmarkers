import datetime
import json
import random

from django.contrib.gis.geos import GEOSGeometry
import factory

from fitmarkers.models import Workout

class WorkoutFactory(factory.Factory):
    FACTORY_FOR = Workout

    provider = Workout.MAPMYFITNESS
    type = Workout.TYPE_RUN
    user_id = factory.LazyAttribute(lambda o: random.randint(1, 50000))
    start_datetime = factory.LazyAttribute(lambda o: datetime.datetime.utcnow())
    provider_id = factory.LazyAttribute(lambda o: random.randint(1, 50000))
    duration = factory.LazyAttribute(lambda o: random.randint(1, 60*60*3))
    geom = factory.LazyAttribute(lambda o: generate_geom(4))
    

def random_coordinate():
    x_coordinate_range = (-105, -95)
    y_coordinate_range = (35, 45)
    return (random.randint(*x_coordinate_range), random.randint(*y_coordinate_range))

def generate_geom(vertices=4):
    linestring = {'type': 'LineString', 'coordinates': [random_coordinate() for i in range(50)]}
    geom = GEOSGeometry(json.dumps(linestring))
    return geom