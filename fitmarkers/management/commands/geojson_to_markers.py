import json

from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand

from fitmarkers.models import Marker


class Command(BaseCommand):
    args = 'geojson_file'
    help = 'Add GeoJSON feature in the geojson file as markers'

    def handle(self, *args, **options):
        for arg in args:
            with open(arg, 'r') as f:
                content = f.read()
                json_content = json.loads(content)
                for feature in json_content['features']:
                    marker = self._feature_to_marker(feature)
                    marker.save()

    def _feature_to_marker(self, feature):
        marker_kwargs = {
            'geom': GEOSGeometry(json.dumps(feature['geometry']))
        }
        if 'name' in feature['properties'] and feature['properties']['name'] is not None and len(feature['properties']['name']):
            marker_kwargs['name'] = feature['properties']['name']
        if 'description' in feature['properties'] and feature['properties']['description'] is not None and len(feature['properties']['description']):
            marker_kwargs['description'] = feature['properties']['description']

        marker = Marker(**marker_kwargs)
        return marker
