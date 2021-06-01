
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
const centroidData = JSON.parse(document.getElementById('centroids').textContent);


// Binds a popup on each point, with cluster size and number of cases
function onEachFeature(feature, layer) {
	var popupText = "";
    if (feature.properties) {
		if (feature.properties.size){
			popupText += "Cluster radius: " + feature.properties.size + "km<br>";
		}
		if (feature.properties.numPoints){
			popupText += "number of cases in cluster: " + feature.properties.numPoints + "<br>";
		}

		layer.bindPopup(popupText);
    }
}

// Define color based on number of points in cluster
function getColor(numPoints){
	numPoints = parseInt(numPoints);
	if (numPoints <= 50){
		return "#00FF00";
	}else if (numPoints <= 100){
		return "#e8aa00";
	}else {
		return "#FF0000";
	}
}

// Add the centroids and circles to the map
if (centroidData){
	L.geoJSON(centroidData, {
		pointToLayer: function (feature, latlng) {
			var size = parseFloat(feature.properties.size) * 1000;
			return L.circle(latlng, {
		radius: size,
		fillColor: getColor(feature.properties.numPoints),
		color: "#000",
		weight: 1,
		fillOpacity: 0.75
	});
		},
		onEachFeature: onEachFeature
	}).addTo(map);
}

