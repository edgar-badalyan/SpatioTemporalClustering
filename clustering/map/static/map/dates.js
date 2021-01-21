
// Get JSON data
const date = JSON.parse(document.getElementById('date').textContent);
const mode = JSON.parse(document.getElementById('mode').textContent);


$("#datepicker" ).datepicker();
 
 // Warning: months are indexed as 0-11 in JS Date class but 1-12 in Python's date.
$('#datepicker').datepicker('setDate', new Date(date["year"], date["month"]-1, date["day"]) );
                                                                                            

$('#datepicker').datepicker().on("input change", function (e) {
	
	var dateText = e.target.value;
	dateText = dateText.replaceAll("/", "-");
	if (mode === "point"){
		var url = "/date/" + dateText;
	}else{
		var url = "/clusters/date/" + dateText;
	}
    window.location.replace(url);
});