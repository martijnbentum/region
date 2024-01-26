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
var current_element = false;
var current_p = false;
var current_div= false;
var highlighted_markers = [];

const red = "#b32d2d";
const green = "#287028";
const blue = "#0202b3";
const yellow = "#c4c400";
const purple = "#800080";
const marker_color = '#4287f5'

const lighterRed = "#FF0000";
const lighterGreen = "#14de4a";
const lighterBlue = "#0000FF";
const lighterYellow = "#FFFF00";
const lighterPurple = "#fa02fa";
const lighterMarkerColor = '#82cbe8';

function make_lighter_color(color) {
    if (color == red) {return lighterRed;}
    if (color == green) {return lighterGreen;}
    if (color == blue) {return lighterBlue;}
    if (color == yellow) {return lighterYellow;}
    if (color == purple) {return lighterPurple;}
    if (color == marker_color) {return lighterMarkerColor;}
    console.log('color not found', color);
    return color;
}

function make_darker_color(color) {
    if (color == lighterRed) {return red;}
    if (color == lighterGreen) {return green;}
    if (color == lighterBlue) {return blue;}
    if (color == lighterYellow) {return yellow;}
    if (color == lighterPurple) {return purple;}
    if (color == lighterMarkerColor) {return marker_color;}
    return color;
}

var layer_dict= {'connection':[]}
var highlighted_elements= [];

console.log('instances');
console.log(instances);
console.log('connection_dict');
console.log(connection_dict);
console.log('instance');
console.log(instance);



function add_links(names, urls, element) {
    for (let i = 0; i<names.length; i++) {
        var a_instance =document.createElement("a");
        element.appendChild(a_instance);
        if (i < names.length -1) {
            var span_instance =document.createElement("span");
            span_instance.textContent = ', ';
            element.appendChild(span_instance);
        }
        console.log('names',names[i], 'urls',urls[i]);
        a_instance.setAttribute('href',urls[i]);
        a_instance.textContent = names[i];
    }
}

var title = document.getElementById('title');
//title.innerHTML = connection_dict.original_title;
add_links([connection_dict.original.title],
    [connection_dict.original.detail_url], title);

var original_div = document.getElementById('original');
original_div.setAttribute('type','original');
original_div.addEventListener('mouseover',on_div_hover);
original_div.addEventListener('mouseout',on_div_leave);
var author = document.getElementById('author');
add_links(connection_dict.original.author_names, 
    connection_dict.original.author_urls, author);
//author.textContent= connection_dict.original_author;
//author.href = connection_dict.original.author_urls[0] 
var genre = document.getElementById('genre_name');
genre.textContent= connection_dict.genre;
var setting= document.getElementById('setting_name');
setting.textContent= connection_dict.original.setting;
var language= document.getElementById('language_name');
language.textContent= connection_dict.original_language;
var publication= document.getElementById('publication');
add_links(connection_dict.original.publication_titles,
    connection_dict.original.publication_urls, publication);
//publication.textContent= connection_dict.original.publication_titles;
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

function find_markers_by_type(type) {
    var output_markers = [];
    var original = false;
    if (type == 'original') {
        type = 'publication';
        original = true;
    }
    for (i = 0; i<layer_dict.connection.length; i++) {
        var marker = layer_dict.connection[i];
        if (marker.options.info.location_type.includes(type)) {
            if (original == true && marker.options.info.original == true) {
                output_markers.push(marker);
            }
            else if (original == false) {
                output_markers.push(marker);
            }
        }
    }
    return output_markers;
}

function find_marker_by_pk(markers,pk) {
    pk = parseInt(pk);
    var output_markers = [];
    for (i = 0; i<markers.length; i++) {
        var marker = markers[i];
        if (marker.options.info.catalogue_Text.includes(pk)) {
            output_markers.push(marker);
        }
    }
    return output_markers;
}

function highlight_markers(markers) {
    for (i = 0; i<markers.length; i++) {
        var marker = markers[i];
        var color = make_lighter_color(marker.options.color);
        marker.setStyle({color:color, fillOpacity:0.8});
        highlighted_markers.push(marker);
    }
}

function darken_markers() {
    for (i = 0; i<highlighted_markers.length; i++) {
        var marker = highlighted_markers[i];
        var color = make_darker_color(marker.options.color);
        marker.setStyle({color:color, fillOpacity:0.3});
    }
    highlighted_markers = [];
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
        var text_pks = e.target.options.info.catalogue_Text;
        for (i = 0; i<text_pks.length; i++) {
            var pk = text_pks[i];
            publication_div = document.getElementById(pk);
            publication_div.classList.add('highlight');
            highlighted_elements.push(publication_div);
        }
    }
    scroll_to_element(highlighted_elements[0]);
}
function on_marker_leave(e) {
    for (i = 0; i<highlighted_elements.length; i++) {
        highlighted_elements[i].classList.remove('highlight');
    }
    highlighted_elements = [];
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
    if (loc.original == true) {var radius = 9;}
    else {var radius = 5;}
	
	marker.setRadius(radius)
	add_marker_behavior(marker);
	layer_dict[layer].push(marker)
	marker.addTo(mymap);
	return marker;
}

var locations = connection_dict.locations;
for (i = 0; i<locations.length; i++) {
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

function make_link_line(line_name,names, urls, line_id, parent_element) {
    var line = document.createElement('p');
    var helper = document.createElement('span');
    line.className = 'body';
    line.id = line_name + ' ' + line_id;
    helper.textContent = line_name + ':';
    helper.className = 'helper';
    line.appendChild(helper);
    parent_element.appendChild(line);
    console.log('names',names, 'urls',urls);
    add_links(names, urls, line);
    }

function add_translation(translation) {
    var translations = document.getElementById('translations');
    var hr= document.createElement('hr');
    var pk = translation.serialized.pk;
    div = document.createElement('div');
    div.id = pk;
    div.setAttribute('type','translation');
    div.addEventListener('mouseover',on_div_hover);
    div.addEventListener('mouseout',on_div_leave);
    make_link_line('title',[translation.title],[translation.detail_url],pk,div);
    make_link_line('author',translation.author_names,translation.author_urls,
        pk,div);
    make_line('language',translation.language,pk,div);
    make_link_line('publication',translation.publication_titles,
        translation.publication_urls,pk,div);
    translations.appendChild(div);
    translations.appendChild(hr);
}

function add_translations() {
    var translations = connection_dict.translations;
    for (let i = 0; i<translations.length; i++) {
            console.log(translations[i], i )
            add_translation(translations[i])
    }
}


console.log('before translations');


add_translations();

function element_to_div(element) {
    var div = element;
    while (div.tagName != 'DIV') {
        div = div.parentElement;
    }
    return div;
}

function find_parent_p(element) {
    if (element == null) {return false;}
    if (element.tagName == 'DIV') {return false;}
    if (element.tagName == 'P') {return false;}
    while (element.tagName != 'P') {
        element = element.parentElement;
    }
    return element;
}


function on_div_hover(e) {
    var element = e.target;
    var p = find_parent_p(element);
    var div = element_to_div(element);
    if (p == current_p) {return false;}
    current_element = element;
    current_p = p;
    current_div = div;
    if (p && p.id == 'author') {
        var markers = find_markers_by_type('author');
        highlight_markers(markers);
    }
    if (p && p.id == 'setting') {
        var markers = find_markers_by_type('setting');
        highlight_markers(markers);
    }
    if (p && p.id.includes('publication')) { 
        if (div.getAttribute('type') == 'original') {
            var markers = find_markers_by_type('original');
            highlight_markers(markers);
        }
        else if (div.getAttribute('type') == 'translation'){
            var markers = find_markers_by_type('publication');
            var markers = find_marker_by_pk(markers, div.id);
            highlight_markers(markers);
        }
    }
} 

function on_div_leave(e) {
    var element = e.target;
    var p = find_parent_p(element);
    var div = element_to_div(element);
    if (p == current_p ) {current_p = false;}
    if (div  == current_div ) {current_div = false;}
    darken_markers();
}


