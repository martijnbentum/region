
// leaflet map setup
var mymap = L.map('mapid').setView([52.0055328,4.67565177],5);
var attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">'
attribution += 'OpenStreetMap contributors &copy; '
attribution += '<a href="https://carto.com/attribution">CARTO</a>'
const tileUrl = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'
const tiles = L.tileLayer(tileUrl,{attribution});
tiles.addTo(mymap);

//global variables
var marker_color = '#4287f5'
var highlight_color = "#e6da09"
var click_color = "#fc0352"
var html_icon = '<a style="color:'+marker_color
html_icon +=';"><i class="fas fa-map-marker-alt"></i></i></a>'
var html_highlight_icon = '<a style="color:'+highlight_color
html_highlight_icon+=';"><i class="fas fa-map-marker-alt"></i></i></a>'
var last_clicked_marker = false;
var last_activated = false;
var last_deactivated = false;
var entries = [];
var icon = L.divIcon({
	className:name,
	html:html_icon,
	iconAnchor:[3,15]
	})

function loc2latlng(loc) {
	//extract latitude and longitude form loc object
	try { latlng = loc.gps.split(',').map(Number); }
	catch {latlng = [] }
	if (latlng.length != 2) {
		return false
	}
	if (typeof(latlng[0]) != 'number' || typeof(latlng[1]) != 'number') {
		return false
	}
	return latlng
	}

	
function add_marker_behavior(marker) {
	// adds marker behavior
	marker.on('mouseover',on_marker_hover)
	marker.on('mouseout',on_marker_leave)
	marker.on('click',on_marker_click)
}

function make_circle_marker(loc,i) {
	//create a marker a circle
	latlng = loc2latlng(loc);
	if (latlng == false) { return false;}
	name = loc.name
	var marker=L.circleMarker(latlng,{color:marker_color,weight:2,
		fillOpacity:0.3,
		className:loc.name, index:i})
	var radius = 4;
	marker.setRadius(radius)
	add_marker_behavior(marker);
	layerDict['circle'].push(marker)
	//marker.addTo(mymap);
	return marker;
}

function make_marker(loc,i) {
	// create a marker icon with the divIcon
	latlng = loc2latlng(loc);
	if (latlng == false) { return false;}
	var marker = L.marker(latlng,{icon:icon, className:loc.name, index:i})
	add_marker_behavior(marker);
	layerDict['icon'].push(marker)
	return marker;
}

function activate_marker(marker) {
	//change the color of a marker to highlight when hovered
	if (marker == last_clicked_marker) { return false}
	try {marker.setStyle({fillColor:highlight_color, color:highlight_color});}
	catch {marker._icon.innerHTML = html_highlight_icon;}
	last_activated = marker;
}
	
function deactivate_marker(marker) {
	//change the color of a marker to default when hovered
	if (marker == last_clicked_marker) { return false}
	if (last_activated == false) { return false }
	try {marker.setStyle({fillColor:marker_color,color:marker_color});}
	catch {marker._icon.innerHTML = html_icon;}
	last_deactivated = marker;
}

function set_marker_clicked(marker) {
	// change color of marker to clicked color
	set_marker_unclicked();
	try {marker.setStyle({fillColor:click_color, color:click_color});}
	catch {marker._icon.innerHTML = html_highlight_icon;}
	last_clicked_marker = marker;
}

function set_marker_unclicked() {
	// change color of marker to default color
	if (last_clicked_marker == false) { return false }
	var marker = last_clicked_marker;
	try {marker.setStyle({fillColor:marker_color,color:marker_color});}
	catch {marker._icon.innerHTML = html_icon;}
	last_clicked_marker = false
}

function show_info(index) {
	// shows general information (number of linked instances) 
	// about a location at the top of the screen
	var label = document.getElementById('city_label');
	if (clustered_marker_indices.includes(index)) {
		var elements = clustered_marker_dict[index].elements;
		var html = ''
		for (let i=0; i < elements.length; i++) {
			var el= elements[i];
			var info = d[el.options.index];
			html += info.name
			html += '<small> (' + info.count + ')</small>';
			if (html.length > 240) {
				html += '<small> [...] + ' + (elements.length - 1 - i) + ' locations'
				break
			}
			if (i != elements.length -1) { html += ', '; }
		}
	} else {
		var info =d[index];
		var html = info.name;
		html += '<small> (' + info.count + ' entries) ';
		for (const x of info.model_names) {
			if (x) { html += x.toLowerCase() + ' '}
		}
		html += '</small>'
	}
	label.innerHTML = html
}

function on_marker_hover(e) {
	//show info and change color of an element on the map when hovered
	deactivate_marker(last_activated);
	activate_marker(this);
	show_info(this.options.index);
}

function on_marker_leave(e) {
	//nothing to do now
}

function on_marker_click(e) {
	// opens sidebar (if closed) removes old elements (if present) 
	// shows instances linked to location in sidebar
	var s = this.options.className;
	set_marker_clicked(this)
	show_sidebar(this.options.index);
	open_right_nav();
}

async function get_instance(instance_id,instance_category) {
	//get information of a single instance via ajax call
	//currently not used
	var path = '/locations/ajax_instance/'
	path += instance_category.replaceAll('_','/') + '/'
	path += instance_id	
	const response = await fetch(path); 
	const data = await response.json()
}

function _add_instance(instance, model_name, city_div) {
	// display a single instance to the sidebar
	// helper function of get_instances
	var dlinks= document.getElementById(model_name + '-links-'+city_div.id);
	a =document.createElement("a");
	dlinks.appendChild(a);
	a.setAttribute('href',instance.detail_url);
	a.innerHTML = instance.name;
	a.classList.add("small_text");
	entries.push(a)
}

async function get_instances(instance_ids,instance_category,city_div) {
	// load instances associated with a given category (e.g. Text) via ajax
	// when a location is clicked this function is used to 
	// retrieve information from server
	var model_name = instance_category.split('_')[1]
	var path = '/locations/ajax_instances/';
	path += instance_category.replaceAll('_','/') + '/';
	path += instance_ids.join(',');	
	const response = await fetch(path); 
	data = await response.json();
	var dall = document.getElementById(model_name + '-all-'+city_div.id);
	var dlinks = document.createElement('div');
	dlinks.id = model_name + '-links-' +city_div.id
	dall.appendChild(dlinks)
	for (const instance of data.instances) {
		_add_instance(instance,model_name, city_div);
	}
}

function show_category(instance_ids, category,city_div) {
	// get category information and create an html element to display it in the sidebar
	// the category (e.g. Text) the corresponding instances are loaded via ajax
	model_name = category.split('_')[1]
	// var sidebar= document.getElementById('sidebar-content');
	var d = document.createElement('div')
	entries.push(d);
	d.id = model_name + '-all-' + city_div.id;
	city_div.appendChild(d);
	get_instances(instance_ids, category, city_div)
	var a =document.createElement("a");
	a.setAttribute('href',"javascript:void(0)");
	a.setAttribute('onclick', 'toggle_sidebar_category(this)');
	a.setAttribute('data-links_id', model_name + '-links-'+city_div.id);
	d.appendChild(a);
	a.innerHTML = model_name + ' <small>(' + instance_ids.length + ')</small>';
	a.classList.add('category-header');
}

function show_categories(info) {
	// show categories (e.g. Text, Person) in the sidebar 
	// linked to a given location 
	var sidebar= document.getElementById('right_sidebar_content');
	var city_div =document.createElement("d");
	sidebar.appendChild(city_div)
	city_div.id = info.pk + "-links";
	entries.push(city_div)
	console.log(city_div)
	for (const [key, instance_ids] of Object.entries(info)) {
		if ('count,model_names,name,gps,pk'.split(',').includes(key)){
		} else {
			show_category(instance_ids, key, city_div);
		}
	}
}

function show_city(info) {
	var sidebar= document.getElementById('right_sidebar_content');
	var div =document.createElement("d");
	sidebar.appendChild(div);
	entries.push(div)
	var a =document.createElement("a");
	a.setAttribute('href',"javascript:void(0)");
	a.setAttribute('onclick', 'toggle_sidebar_category(this)');
	a.setAttribute('data-links_id', info.pk + '-links');
	a.setAttribute('data-color_inactive', 'grey');
	a.setAttribute('data-color_active', '#2f3030');
	a.classList.add("city-header");
	div.appendChild(a);
	// var title = document.getElementById('title');
	var html = info.name;
	html += '<small> (' + info.count + ' entries) ' + '</small>';
	a.innerHTML = html
	show_categories(info);
}

function clear_sidebar() {
	//remove old entries from sidebar
	var sidebar= document.getElementById('right_sidebar_content');
	for (const x of entries) {
		x.remove()
	}
	entries = [];
}

function show_sidebar(index) {
	//show sidebar with entries from selected location
	clear_sidebar();
	if (clustered_marker_indices.includes(index)) {
		var elements = clustered_marker_dict[index].elements;
		console.log(elements)
		for (let i=0; i < elements.length; i++) {
			var el= elements[i];
			var info = d[el.options.index];
			show_city(info)
		}
	} else {
		var info =d[index];
		show_city(info)
	}
}

function toggle_sidebar_category(element) {
	//hide reveal category items (e.g. Text) from sidebar
	var dlinks = document.getElementById(element.dataset.links_id);
	console.log(element,dlinks)
	if (dlinks.style.display == "") {
		element.style.color = element.data_color_inactive;//"grey";
		dlinks.style.display = "none";
	} else {
		element.style.color = element.data_color_active;//"#2f3030";
		dlinks.style.display = "";
	}
}

function show_markers(markers, make_point = true) {
	//var controlLayers;
	hide_markers(markers);
	for (i = 0; i<markers.length; i++) {
		var marker = markers[i];
		if (make_point) {
			marker.addTo(mymap);
		} else if ( clustered_marker_indices.includes(marker.options.index) ) {
			if (clustered_marker_dict[marker.options.index].plotted) {
				continue;
			}
			clustered_marker_dict[marker.options.index].center_element.addTo(mymap);
			clustered_marker_dict[marker.options.index].plotted = true;
		} else {
			marker.addTo(mymap);
		}
	}
}

function update_markers(markers) {
	show_markers(layerDict['circle'], make_point = true);
	[clustered_marker_dict, clustered_marker_indices] = cluster(c)
	show_markers(layerDict['circle'], make_point = false);
}



function hide_markers(markers) {
	//var controlLayers;
	for (i = 0; i<markers.length; i++) {
		var marker = markers[i];
		marker.remove();
	}
}


// layerdict contains the circle and icon markers
// for now only the circle markers are made
var names = 'circle,icon'.split(',');
layerDict = {}
for (var i = 0; i<names.length; i++) {
	layerDict[names[i]] = []
}

//cluster markers based on overlap
var c = layerDict['circle'];

// the d element contains all information linking locations to instances
var d= JSON.parse(document.getElementById('d').textContent);
var d = Object.values(d)
for (i = 0; i<d.length; i++) {
	make_circle_marker(d[i],i);
	//make_marker(d[i],i);
}

var controlLayers;
var overlayMarkers= {};
var clustered_markers = [];
var clustered_marker_indices = [];
var clustered_marker_dict = {};
show_markers(layerDict['circle']);
c.sort(sort_on_x);
update_markers(layerDict['circle']);

function open_left_nav() {
	// open sidebar
	document.getElementById("left_sidebar").style.width = "320px";
	document.getElementById("content").style.marginLeft = "323px";
}

function close_left_nav() {
	// close sidebar
	document.getElementById("left_sidebar").style.width = "0px";
	document.getElementById("content").style.marginLeft = "25px";
}

function open_right_nav() {
	// open sidebar
	document.getElementById("right_sidebar").style.width = "400px";
	document.getElementById("content").style.marginRight = "403px";
}

function close_right_nav() {
	// close sidebar
	document.getElementById("right_sidebar").style.width = "0px";
	document.getElementById("content").style.marginRight= "25px";
}


mymap.on('zoomend', function() {
	// update the clustering after zooming in or out
	console.log('zoomed')
	console.log(c);
	update_markers(layerDict['circle']);
});

open_left_nav();