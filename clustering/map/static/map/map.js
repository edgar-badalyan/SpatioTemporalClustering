
// Set up map
var map = L.map('mapid').setView([50.81301, 4.37613], 14);

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw'
}).addTo(map);

	
// Get JSON data
const pointData = JSON.parse(document.getElementById('point_data').textContent);
const centroidData = JSON.parse(document.getElementById('centroids').textContent);


// Global variables
STATES = ["POSITIVE", "NEGATIVE", "RECOVERED"];
NO_CLUSTER_COLOR = "#FF0000" 
COLORS = ["#0000FF", "#FFFF00", "#FF6600", "#00FF00", "#6600FF", "#000000", "#FFFFFF"]


// Defines the style for a point, depending on the cluster it belongs to
function geojsonMarkerOptions(feature){
	
	var clusterId = parseInt(feature.properties.cluster);
	if(clusterId === -1){
		var colorId = NO_CLUSTER_COLOR;
	}else{
		var colorId = COLORS[clusterId%7];
	}
	var geojsonMarkerOptions = {
		radius: 5,
		fillColor: colorId,
		color: "#000",
		weight: 1,
		fillOpacity: 0.8
	};
	
	return geojsonMarkerOptions;
}


// Binds a popup on each point, with cluster id, state, and date
function onEachFeature(feature, layer) {
	var popupText = "";
    if (feature.properties) {
		if (feature.properties.cluster){
			popupText += "Cluster: " + feature.properties.cluster + "<br>";
		}
		if (feature.properties.state){
			popupText += "State: " + STATES[feature.properties.state-1] + "<br>";
		}
		if (feature.properties.date){
			popupText += "Date: " + feature.properties.date;
		}	
		layer.bindPopup(popupText);
    }
}


// Add the points to the map
L.geoJSON(pointData, {
    pointToLayer: function (feature, latlng) {
        return L.circleMarker(latlng, geojsonMarkerOptions(feature));
    },
	onEachFeature: onEachFeature
}).addTo(map);


// If cluster mode, add the centroids to the map
if (centroidData){
	L.geoJSON(centroidData, {
		pointToLayer: function (feature, latlng) {
			return L.circleMarker(latlng, {
		radius: 8,
		fillColor: "#007000",
		color: "#000",
		weight: 1,
		fillOpacity: 0.9
	});
		},
		onEachFeature: onEachFeature
	}).addTo(map);
}


// Open popup when the map is clicked.
var popup = L.popup();

function onMapClick(e) {
    popup
        .setLatLng(e.latlng)
        .setContent("You clicked the map at " + e.latlng.toString())
        .openOn(map);
}

map.on('click', onMapClick);

