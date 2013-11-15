lvector.FitMarkers = lvector.GeoJSONLayer.extend({
    initialize: function(options) {

        // Check for required parameters
        for (var i = 0, len = this._requiredParams.length; i < len; i++) {
            if (!options[this._requiredParams[i]]) {
                throw new Error("No \"" + this._requiredParams[i] + "\" parameter found.");
            }
        }

        // Extend Layer to create FitMarkers
        lvector.Layer.prototype.initialize.call(this, options);

        // _globalPointer is a string that points to a global function variable
        // Features returned from a JSONP request are passed to this function
        this._globalPointer = "FitMarkers_" + Math.floor(Math.random() * 100000);
        window[this._globalPointer] = this;

        // Create an array to hold the features
        this._vectors = [];

        if (this.options.map) {
            if (this.options.scaleRange && this.options.scaleRange instanceof Array && this.options.scaleRange.length === 2) {
                var z = this.options.map.getZoom();
                var sr = this.options.scaleRange;
                this.options.visibleAtScale = (z >= sr[0] && z <= sr[1]);
            }
            this._show();
        }
    },

    options: {},

    _requiredParams: [],

    _getFeatures: function() {
        // Build URL
        url = "/markers/?bbox=" + this.options.map.getBounds().toBBoxString();

        var me = this;

        $.ajax({
            url: url,
            type: 'GET',
            success: function (data) {
                var goodFeatures = {type: 'FeatureCollection', features: []};
                for (var _feature in data.features) {
                    feature = data.features[_feature];
                    if (fm.excludeIds.indexOf(feature.properties.id) < 0) {
                        goodFeatures.features.push(feature);
                    }
                }
                me._processFeatures(goodFeatures);
            }
        });
    }

});

(function() {
    var excludeIds = [];
    for (var _wm in fm.monthly_markers.features) {
        wm = fm.monthly_markers.features[_wm];
        excludeIds.push(wm.properties.marker_id);
    }
    fm.excludeIds = excludeIds;
    var mediumIconLight = L.icon({
        iconUrl: 'http://api.tiles.mapbox.com/v3/marker/pin-m+94b7cb.png',
        iconSize: [30, 70],
        iconAnchor: [16, 37],
        popupAnchor: [0, -28]
    });
    var mediumIconDark = L.icon({
        iconUrl: 'http://api.tiles.mapbox.com/v3/marker/pin-m+192e3a.png',
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
        monthly_markers_layer = new L.GeoJSON(fm.monthly_markers, {
            pointToLayer: function (feature, latLng) {
                return L.marker(latLng, {icon: mediumIconDarkStar});
            }
        });
    map
        .addLayer(monthly_markers_layer)
        .fitBounds(monthly_markers_layer.getBounds());
    L.control.layers({'Road': road_layer, 'Satellite': satellite_layer}, null).addTo(map);
    fitmarkers_layer = new lvector.FitMarkers({
        map: map,
        scaleRange: [12, 18],
        symbology: {
            type: 'single',
            vectorOptions: {
                icon: mediumIconDark
            }
        }
    });
}());