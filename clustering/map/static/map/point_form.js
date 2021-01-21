var latlng_radio = document.querySelector("#latlng");
var addr_radio = document.querySelector("#addr");

latlng_radio.addEventListener('change', radioChange);

addr_radio.addEventListener('change', radioChange);

function radioChange(e){
	console.log("test");
	switch(e.target.id){
		case 'latlng':
			window.location.replace("/new_coord"); break;
		case 'addr':
			window.location.replace("/new_addr"); break;
	}
}
