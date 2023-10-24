var mymap = L.map('mapid').setView([52.0055328,4.67565177],5);
var attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">'
attribution += 'OpenStreetMap contributors &copy; '
attribution += '<a href="https://carto.com/attribution">CARTO</a>'
const tileUrl = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'
const tiles = L.tileLayer(tileUrl,{attribution});
tiles.addTo(mymap);


var instances = JSON.parse(document.getElementById('instances').textContent);
var connection_dict= JSON.parse(document.getElementById('connection_dict').textContent);
var instance= JSON.parse(document.getElementById('instance').textContent);
var instance= JSON.parse(instance)[0];

const red = "#FF0000";
const green = "#008000";
const blue = "#0000FF";
const yellow = "#FFFF00";
const purple = "#800080";

var marker_color = '#4287f5'
var layer_dict= {'connection':[]}
var highlighted_elements= [];

console.log('instances');
console.log(instances);
console.log('connection_dict');
console.log(connection_dict);
console.log('instance');
console.log(instance);

var title = document.getElementById('title');
title.innerHTML = connection_dict.original_title;

var author = document.getElementById('author_name');
author.textContent= connection_dict.original_author;
var genre = document.getElementById('genre_name');
genre.textContent= connection_dict.genre;
var setting= document.getElementById('setting_name');
setting.textContent= connection_dict.original.setting;
var language= document.getElementById('language_name');
language.textContent= connection_dict.original_language;
var publication= document.getElementById('publication_names');
publication.textContent= connection_dict.original.publication_titles;
var year= document.getElementById('year_names');
year.textContent= connection_dict.original.publication_years;

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

function scroll_to_element(element) {
    element.scrollIntoView({
        behavior: "smooth", 
        block: "center", 
        inline: "nearest"});
}

function on_marker_hover(e) {
    if (e.target.options.info.location_type.includes('author')) { 
        author_line = document.getElementById('author');
        author_line.classList.add('highlight');
        highlighted_elements.push(author_line);
    }
    else if (e.target.options.info.location_type.includes('setting')) { 
        setting_line = document.getElementById('setting');
        setting_line.classList.add('highlight');
        highlighted_elements.push(setting_line);
    }
    else if (e.target.options.info.original) {
        original_div = document.getElementById('original');
        original_div.classList.add('highlight');
        highlighted_elements.push(original_div);
    }
    else if (e.target.options.info.location_type.includes('publication')) {
        console.log(e.target.options.info, 'publication')
        var text_pks = e.target.options.info.catalogue_Text;
        for (i = 0; i<text_pks.length; i++) {
            var pk = text_pks[i];
            publication_div = document.getElementById(pk);
            publication_div.classList.add('highlight');
            highlighted_elements.push(publication_div);
        }
    }
    scroll_to_element(highlighted_elements[0]);
    console.log('hover',e, e.target.options.info.location_type)
}
function on_marker_leave(e) {
    for (i = 0; i<highlighted_elements.length; i++) {
        highlighted_elements[i].classList.remove('highlight');
    }
    highlighted_elements = [];
    console.log('leave ',e)
}
function on_marker_click(e) {
    console.log('click',e)
}

function get_marker_color(loc) {
    if (loc.location_type.includes('setting')) {
        return green
    }
    if (loc.location_type.includes('publication')) {
        return marker_color
    }
    if (loc.location_type.includes('author')) {
        return red 
    }
    return purple
}

function make_circle_marker(loc,i, layer ) {
	//create a marker a circle
	var latlng = loc2latlng(loc);
	if (latlng == false) { return false;}
    var color = get_marker_color(loc);
	var marker=L.circleMarker(latlng,{
        color:color,
        weight:2,
		fillOpacity:0.3,
		className:loc.name, 
        location_pk:loc.pk,
        info:loc,
        index:i,
        visible:'active'})
    if (loc.original == true) {var radius = 6;}
    else {var radius = 3;}
	
	marker.setRadius(radius)
	add_marker_behavior(marker);
	layer_dict[layer].push(marker)
	marker.addTo(mymap);
	return marker;
}

var locations = connection_dict.locations;
for (i = 0; i<locations.length; i++) {
        //console.log(locations[i], i, 1111)
        make_circle_marker(locations[i],i,'connection')
}

function make_line(line_name, line_content,line_id, parent_element) {
    var line = document.createElement('p');
    var helper = document.createElement('span');
    var content= document.createElement('span');
    line.className = 'body';
    helper.textContent = line_name + ': ';
    helper.className = 'helper';
    content.textContent = line_content;
    line.id = line_name + ' ' + line_id;
    line.appendChild(helper);
    line.appendChild(content);
    parent_element.appendChild(line);
}

function add_translation(translation) {
    var translations = document.getElementById('translations');
    var hr= document.createElement('hr');
    var pk = translation.serialized.pk;
    div = document.createElement('div');
    div.id = pk;
    make_line('title',translation.title,pk,div);
    make_line('author',translation.author,pk,div);
    make_line('language',translation.language,pk,div);
    make_line('publication',translation.publication_titles,pk,div);
    translations.appendChild(div);
    translations.appendChild(hr);
}

function add_translations() {
    console.log('hello');
    var translations = connection_dict.translations;
    for (i = 0; i<translations.length; i++) {
            console.log(translations[i], i )
            add_translation(translations[i])
    }
}

console.log('before translations');


add_translations();



