from django.contrib.gis.geos.polygon import Polygon


def query_args_bbox(bbox_string):
    bbox = bbox_string.split(',')

    return {
        'geom__intersects': Polygon.from_bbox(bbox)
    }
