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
            zoom: 10,
            layers: [
                road_layer
            ]
        }),
        monthly_markers_layer = new L.GeoJSON(null, {
            pointToLayer: function (feature, latLng) {
                return L.marker(latLng, {icon: mediumIconDarkStar});
            }
        }),
        first_run = true;
    
    map.addLayer(monthly_markers_layer);
    
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

    function getMonthlyMarkers() {
        fitmarkers_layer._hide();
        monthly_markers_layer.clearLayers();
        var activity_type = $('#select-activity').find('li.active').data('type'),
            url = '/user/monthly_workouts/';
        if (activity_type !== 'all') {
            url += '?activity_type=' + activity_type;
        }
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                var excludeIds = [];
                for (var _wm in data.markers_geojson.features) {
                    wm = data.markers_geojson.features[_wm];
                    excludeIds.push(wm.properties.marker_id);
                }
                fm.excludeIds = excludeIds;
                monthly_markers_layer.addData(data.markers_geojson);
                if (first_run) {
                    map.fitBounds(monthly_markers_layer.getBounds());
                    first_run = false;
                }
                fitmarkers_layer._show();
            },
            error: function () {

            }
        });
    }

    $(document).on('ready', function () {
        $('.selector').find('a.select').on('click', function (event) {
            event.preventDefault();
            var $this = $(this),
                $parent = $this.parent();
            if ($parent.hasClass('active')) {
                return;
            } else {
                $this.parent().addClass('active').siblings().removeClass('active');
                getMonthlyMarkers();
            }
        });
    });

    getMonthlyMarkers();
}());
