(function() {
    var mediumIconLight = L.icon({
        iconUrl: 'http://api.tiles.mapbox.com/v3/marker/pin-m+94b7cb.png',
        iconSize: [30, 70],
        iconAnchor: [16, 37],
        popupAnchor: [0, -28]
    });
    var mediumIconDarkStar = L.icon({
        iconUrl: 'http://api.tiles.mapbox.com/v3/marker/pin-m-star+192e3a.png',
        iconSize: [30, 70],
        iconAnchor: [16, 37],
        popupAnchor: [0, -28]
    });
    var road_layer = new L.TileLayer('http://{s}.tiles.mapbox.com/v3/jcsanford.map-qh86l7s4/{z}/{x}/{y}.png', {
                maxZoom: 18,
                subdomains: ['a', 'b', 'c', 'd'],
                attribution: 'Map data (c) <a href="http://www.openstreetmap.org/" target="_blank">OpenStreetMap</a> contributors, CC-BY-SA.'
            }),
        satellite_layer = new L.TileLayer('http://{s}.tiles.mapbox.com/v3/jcsanford.map-c487ey3y/{z}/{x}/{y}.png', {
                maxZoom: 18,
                subdomains: ['a', 'b', 'c', 'd'],
                attribution: 'Map data (c) <a href="http://www.openstreetmap.org/" target="_blank">OpenStreetMap</a> contributors, CC-BY-SA.'
            }),
        map = new L.Map('map-container', {
            center: [40, -100],
            zoom: 18,
            layers: [
                road_layer
            ]
        }),
        workout_layer = new L.GeoJSON(fm.workout, {
            style: {
                color: '#192e3a',
                opacity: 0.8
            }
        });
        workout_markers_layer = new L.GeoJSON(fm.workout_markers, {
            pointToLayer: function (feature, latLng) {
                return L.marker(latLng, {icon: mediumIconDarkStar});
            }
        });
    map
        .addLayer(workout_layer)
        .addLayer(workout_markers_layer)
        .fitBounds(workout_layer.getBounds());
    L.control.layers({'Road': road_layer, 'Satellite': satellite_layer}, null).addTo(map);
}());