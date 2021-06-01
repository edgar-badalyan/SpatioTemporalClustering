
// Get JSON data
const date = JSON.parse(document.getElementById('date').textContent);
const mode = JSON.parse(document.getElementById('mode').textContent);

const datepicker = $("#datepicker");

datepicker.datepicker();
 
 // Warning: months are indexed as 0-11 in JS Date class but 1-12 in Python's datetime library.
datepicker.datepicker('setDate', new Date(date["year"], date["month"]-1, date["day"]) );
                                                                                            

// Listening to date changes
datepicker.datepicker().on("input change", function (e) {
	let url;
	let dateText = e.target.value;
	dateText = dateText.replaceAll("/", "-");
	if (mode === "point"){
		url = "/points/date/" + dateText;
	}else{
		url = "/clusters/date/" + dateText;
	}
    window.location.replace(url);
});


// Handling mode changes
function changeMode(newMode){
	if (mode !== newMode) {
		let dateText = datepicker.val();
		dateText = dateText.replaceAll("/", "-");
		const url = "/" + newMode + "/date/" + dateText;
		window.location.replace(url);
	}
}

function clusterMode(){
	changeMode("clusters");
}

function pointMode(){
	changeMode("points");
}