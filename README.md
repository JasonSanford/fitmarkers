## Leaderboards

Redis Sorted Sets act as leaderboards. The users' point value will servce as the redis score. Set keys look like `activity_all:timespan_all` or `activity_ride:timespan_nov2013`.

Leaderboards needed

Activity / Timespan
All / All
Run / All
Ride / All
Walk / All

All / Month
Run / Month
Ride / Month
Walk / Month

## Dependencies

### System

* PostgreSQL/PostGIS
* GEOS, GDAL, Proj
* Redis - Installed using instructions from http://jasdeep.ca/2012/05/installing-redis-on-mac-os-x/

### Python

#### Runtime

See `requirements.txt` - `pip install -r requirements.txt`

#### Testing

Some additional libraries are used for tests. For now:

    coverage

## Importing Markers

For now marker creation is manual. Markers are maintained in https://github.com/JasonSanford/markers and edited in http://geojson.io.

To add new markers, first `truncate cascaded` the `fitmarkers_marker` table. Then:

    curl -O https://raw.github.com/JasonSanford/markers/master/markers.geojson
    python manage.py geojson_to_markers markers.geojson

## Testing

See testing dependencies above for required libraries. To run tests:

    python manage.py test fitmarkers

To get a coverage report, `pip install coverage` then:

    coverage run manage.py test fitmarkers
    coverage report -m
