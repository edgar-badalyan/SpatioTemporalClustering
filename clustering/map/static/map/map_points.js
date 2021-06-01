
// Set up map
const map = L.map('mapid',
	{zoomSnap:0.5,
	 zoomDelta:0.5}).setView([50.81301, 4.37613], 14);

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

// Global variables
STATES = ["POSITIVE", "NEGATIVE", "RECOVERED"];

// Defines the style for a point
function geojsonMarkerOptions(feature){

	return {
		radius: 5,
		fillColor: "#FF0000",
		color: "#000",
		weight: 1,
		fillOpacity: 0.8
	};
}


// Binds a popup on each point, with state and date
function onEachFeature(feature, layer) {
	var popupText = "";
    if (feature.properties) {
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


