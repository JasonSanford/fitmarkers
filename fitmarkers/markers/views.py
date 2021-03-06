import json

from django.http import HttpResponse, HttpResponseBadRequest

from models import Marker
from utils import query_args_bbox

def search(request):
    filter_kwargs = {}
    
    if 'bbox' in request.GET:
        spatial_args = query_args_bbox(request.GET['bbox'])
    else:
        return HttpResponseBadRequest

    filter_kwargs.update(spatial_args)

    markers = Marker.objects.filter(**filter_kwargs).geojson()
    json_features = [
        {
            'type': 'Feature',
            'properties': {
                'name': marker.name,
                'point_value': marker.point_value,
                'description': marker.description,
                'id': marker.id,
            },
            'geometry': json.loads(marker.geojson),
            'id': marker.id,
        } for marker in markers
    ]
    response = {'type': 'FeatureCollection', 'features': json_features, 'count': len(markers)}

    content = json.dumps(response)
    content_type = 'application/json'

    if 'callback' in request.GET and len(request.GET['callback']):
        content = '{0}({1})'.format(request.GET['callback'], content)
        content_type = 'text/javascript'

    return HttpResponse(content, content_type=content_type)
