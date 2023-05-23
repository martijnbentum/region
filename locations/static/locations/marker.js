//module to handle creation and 'on' methods (on_click, on_hover etc)
import {
    open_right_nav
} from './utils.js';

var last_clicked_marker = false;
var last_activated = false;
var last_deactivated = false;
var marker_color = '#4287f5'
var highlight_color = "#e6da09"
var click_color = "#fc0352"
var clustered_marker_indices = [];
var clustered_marker_dict = {};

function loc2latlng(loc) {
	//extract latitude and longitude form loc object
	try { var latlng = loc.gps.split(',').map(Number); }
	catch {var latlng = [] }
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

function make_circle_marker(loc,i, layer , layerDict) {
	//create a marker a circle
	var latlng = loc2latlng(loc);
    // console.log(loc,latlng)
	if (latlng == false) { return false;}
	name = loc.name
	var marker=L.circleMarker(latlng,{color:marker_color,weight:2,
		fillOpacity:0.3,
		className:loc.name, index:i,visible:'active'})
	var radius = 4;
	marker.setRadius(radius)
	add_marker_behavior(marker);
	layerDict[layer].push(marker)
	//marker.addTo(mymap);
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

function on_marker_hover(e) {
	//show info and change color of an element on the map when hovered
	deactivate_marker(last_activated);
	activate_marker(this);
    console.log(this,'this marker');
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
	show_right_sidebar(this.options.index);
	open_right_nav();
}


var d= JSON.parse(document.getElementById('d').textContent);
//'overview,connection_view'.split(',');

class Markers {
    constructor(layer_name, layerDict) {
        this.layer_name = layer_name
        this.layerDict = layerDict;
        this.markers= [];
        this.d = Object.values(d)
        this.connection_d = false;
        this.make_markers()
    }

    make_markers() {
        for (i = 0; i<this.d.length; i++) {
            let m = make_circle_marker(d[i],i,'overview',this.layerDict);
            this.markers.push(m); 
        }
    }
}




export {
    make_circle_marker,
    on_marker_click,
    on_marker_hover,
    clustered_marker_dict,
    clustered_marker_indices,
    Markers
}
