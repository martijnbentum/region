import {cluster, sort_on_x} from './cluster_rf.js';

import {
    pks_and_category_to_identifiers,
    intersection,
} from './utils.js';

import {
    on_marker_hover,
    on_marker_click,
    Markers,
} from './marker.js';

import {Map_info} from './map_info.js'
import {Info} from './info.js'
import {
    open_left_sidebar,
    open_right_sidebar,
    close_right_sidebar,
    close_left_sidebar,
    } from './sidebar.js'

    
var map_info = new Map_info();
var info = new Info();
var markers = new Markers(map_info);



function set_location_type() {
    //console.log(location_type,location_type.value);
    update_right_sidebar();
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
    console.log(instance,model_name,city_div,'<---')
      
    var location_pk = parseInt(city_div.id.split('-')[0]);
    if (info.filter_active_dict['locationtype'] == 'active'){
        // adding instance (not filtering on locationtype)
    } else if (!'Text,Publication,Illustration'.split(',').includes(model_name)) {
        console.log('this should not occur',model_name,'should be filtered out')
    } else if (info.filter_active_dict['locationtype,setting'] == 'active') {
        if (!instance['setting_location_pks'].includes(location_pk)) {
            //this instance is not linked as setting location, skipping
            return
        }
    } else if (info.filter_active_dict['locationtype,publication'] == 'active') {
        if (!instance['publication_location_pks'].includes(location_pk)) {
            //this instance is not linked as publication location, skipping
            return
        }
    }
	var dlinks= document.getElementById(model_name + '-links-'+city_div.id);
    var line_div = document.createElement('div')
	line_div.classList.add("instance_line_div");
	dlinks.appendChild(line_div);
	var a_instance =document.createElement("a");
	line_div.appendChild(a_instance);
	a_instance.setAttribute('href',instance.detail_url);
    var m = instance.name ;
    if (model_name == 'Text') {
        m += ' <span class="language" >(' +instance.language + ')</span>' ;
    } else if (model_name == 'Publication') {
        console.log(instance)
        m += ' <span class="language" >(' +instance.language;
        if (instance.language != '') {
            m += ' | ' 
        }
        m += instance.publication_type 

        if (instance.years.length == 1) {
            m += ' | ' + instance.years[0]
        }
        m +=')</span>';
    }
	a_instance.classList.add("small_text");
	a_instance.classList.add("title_link");
    a_instance.innerHTML = m;

    if (instance.connection_count && instance.connection_count > 0) {
        var a_links =document.createElement("a");
        line_div.appendChild(a_links);
        a_links.classList.add("small_text");
        a_links.setAttribute('href','#');
        var t = '<i class="fas fa-project-diagram links_link">'
        t += ' (' + instance.connection_count + ')';
        a_links.innerHTML = t;
        if (model_name == 'Text') {
            let f = "get_connections('" + instance.identifier + "')"
            a_links.setAttribute('onclick',f);
            // console.log('con:',instance, model_name)
        }
    }

	info.entries.push(a_instance)
}

async function get_connections(instance_identifier) {
	var path = '/locations/ajax_get_connections/'
	path += instance_identifier.replaceAll('_','/') 
    console.log('c path',path)
	const response = await fetch(path); 
	const data = await response.json()
    console.log('connection data', data, 
        data.instances, data.instances.length);
    markers.hide_markers(markers.layerDict['overview']);
    close_left_sidebar();
    clear_right_sidebar();
    markers.connection_d = Object.values(data.instances);
    for (i = 0; i<markers.connection_d.length; i++) {
            console.log(markers.connection_d[i], i, 1111)
            markers.make_circle_marker(markers.connection_d[i],i,'connection_view')
    }
    markers.update_markers(layerDict['connection_view'])
    console.log(markers.clustered_marker_dict,markers.clustered_marker_indices,'cmd,cmi');
    var group = new L.featureGroup(layerDict['connection_view'])
    map_info.map.fitBounds(group.getBounds().pad(.1))
    info.connection_view = true;
    right_sidebar_connection_view_text(data)
}

async function get_instances(instance_ids,instance_category,city_div) {
	// load instances associated with a given category (e.g. Text) via ajax
	// when a location is clicked this function is used to 
	// retrieve information from server
	var model_name = instance_category.split('_')[1]
	var path = '/locations/ajax_instances/';
	path += instance_category.replaceAll('_','/') + '/';
	path += instance_ids.join(',');	
    console.log('path',path)
	const response = await fetch(path); 
	const data = await response.json();
	var dall = document.getElementById(model_name + '-all-'+city_div.id);
	var dlinks = document.createElement('div');
	dlinks.id = model_name + '-links-' +city_div.id
	dall.appendChild(dlinks)
	for (const instance of data.instances) {
        if (info.active_ids.includes(instance.identifier)) {
            _add_instance(instance,model_name, city_div);
        }
	}
    //console.log(dlinks)
    var ninstances = dlinks.childElementCount;
    if (ninstances != info.right_sidebar_category_counts[model_name]) {
        //console.log(ninstances, right_sidebar_category_counts[model_name])
        var a_id = model_name + 'category-toggle-' + city_div.id;
        var a = document.getElementById(a_id);
        a.innerHTML = model_name + ' <small>(' + ninstances + ')</small>';
    }
}


function count_active_identifiers(identifiers) {
    var count = 0;
    for (const identifier of identifiers) {
        if (info.active_ids.includes(identifier)) { count += 1;}
    }
    return count;
}

function show_category(instance_ids, category,city_div) {
	// get category information and create an html element to 
    //display it in the sidebar
	// the category (e.g. Text) the corresponding instances are loaded via ajax
	var model_name = category.split('_')[1]
    if (info.filter_active_dict['model,'+model_name] == 'inactive') { return; }
	var identifiers=pks_and_category_to_identifiers(instance_ids,category);
    var count_active = count_active_identifiers(identifiers) 
    if (count_active == 0) { return;}
	// var sidebar= document.getElementById('sidebar-content');
	var div = document.createElement('div')
	info.entries.push(div);
	div.id = model_name + '-all-' + city_div.id;
	city_div.appendChild(div);
    //console.log(instance_ids)
	get_instances(instance_ids, category, city_div)
	var a =document.createElement("a");
    a.id = model_name + 'category-toggle-' + city_div.id
	a.setAttribute('href',"javascript:void(0)");
	a.setAttribute('onclick', 'toggle_sidebar_category(this)');
	a.setAttribute('data-links_id', model_name + '-links-'+city_div.id);
	var identifiers=pks_and_category_to_identifiers(instance_ids,category);
	a.setAttribute('data-identifiers',identifiers);
	div.appendChild(a);
	a.innerHTML = model_name + ' <small>(' + count_active + ')</small>';
	a.classList.add('category-header');
    info.right_sidebar_category_counts[model_name] = count_active;
}

function show_categories(information) {
	// show categories (e.g. Text, Person) in the sidebar 
	// linked to a given location 
	var sidebar= document.getElementById('right_sidebar_content');
	var city_div =document.createElement("d");
	sidebar.appendChild(city_div)
	city_div.id = information.pk + "-links";
	info.entries.push(city_div)
	for (const [key, instance_ids] of Object.entries(information)) {
		if ('count,model_names,name,gps,pk,identifiers'.split(',').includes(key)){
		} else {
			show_category(instance_ids, key, city_div);
		}
	}
}

function show_city(information) {
	//show all information linked to specific location
	var sidebar= document.getElementById('right_sidebar_content');
	var div =document.createElement("d");
	sidebar.appendChild(div);
	info.entries.push(div)
	var a =document.createElement("a");
	a.setAttribute('href',"javascript:void(0)");
	a.setAttribute('onclick', 'toggle_sidebar_category(this)');
	a.setAttribute('data-links_id', information.pk + '-links');
	a.setAttribute('data-color_inactive', 'grey');
	a.setAttribute('data-color_active', '#2f3030');
	a.classList.add("city-header");
	div.appendChild(a);
	// var title = document.getElementById('title');
	var html = information.name;
	html += '<small> (' + information.count + ' entries) ' + '</small>';
	a.innerHTML = html
	show_categories(information);
}

function clear_right_sidebar() {
	//remove old entries from sidebar
	var sidebar= document.getElementById('right_sidebar_content');
	for (const x of info.entries) {
		x.remove()
	}
	info.entries = [];
}

function _add_connection_instance_info(instance_dict, original) {
    //show an instance in the text connection view right side bar
    //this can be the original text or a translation or review
    var instance = instance_dict;
	var sidebar= document.getElementById('right_sidebar_content');
    var div = document.createElement('div');
    info.entries.push(div);
    sidebar.append(d)
	var text_title =document.createElement("p");
	var setting =document.createElement("p");
	var genre =document.createElement("p");
	var publication=document.createElement("p");
	var author=document.createElement("p");
	var language=document.createElement("p");
	var hr =document.createElement("hr");
    div.append(text_title)
    if (original) {div.append(hr)}
    if (original) {div.append(genre)}
    div.append(author)
    div.append(publication)
    if (original) {div.append(setting)}
    div.append(language)

	if (original) {text_title.classList.add("title_text");}
	else {text_title.classList.add("small_title_text");}
    text_title.innerHTML = instance.title;
	setting.classList.add("connection_text");
    setting.innerHTML = '<b>Setting</b>: ' +instance.setting
	publication.classList.add("connection_text");
    publication.innerHTML='<b>Published in</b>: '+instance.publication_years_str;
	author.classList.add("connection_text");
    author.innerHTML = '<b>Author</b>: ' +instance.author;
	genre.classList.add("connection_text");
    genre.innerHTML = '<b>Genre</b>: ' +instance.genre;
	language.classList.add("connection_text");
    language.innerHTML = '<b>Language</b>: ' +instance.language;
}

function _add_other_connection_info(instance_dicts, other_name) {
    //show translations or reviews related to a text
	var sidebar= document.getElementById('right_sidebar_content');
    var div = document.createElement('div');
    info.entries.push(div);
    sidebar.append(div)
    if (instance_dicts.length == 0) { return }
	var name=document.createElement("p");
	var hr =document.createElement("hr");
    div.append(name)
    div.append(hr)
	name.classList.add("connection_category");
    name.innerHTML = other_name;
    for (let i=0; i < instance_dicts.length; i++) {
        _add_connection_instance_info(instance_dicts[i]);
    }
}

function back_to_overview() {
    console.log('back to overview');
    clear_right_sidebar();
    markers.hide_markers(markers.layerDict['connection_view']);
    markers.layerDict['connection_view'] = [];
    open_left_sidebar();
    markers.update_markers(markers.active_markers);
    show_right_sidebar(info.right_sidebar_index);    
    console.log('rsi',info.right_sidebar_index);
    info.connection_view = false;
}

function _add_back_to_overview_button() {
	var back= document.getElementById('back_to_overview');
	var a_instance=document.createElement("a");
    back.append(a_instance);
    var t = '<i class="fa fa-reply">'
    a_instance.innerHTML = t;
    f = "back_to_overview()"
    a_instance.setAttribute('href','#');
	a_instance.setAttribute('onclick',f);
	a_instance.classList.add("closebtn");
    info.entries.push(a_instance);
}


function right_sidebar_connection_view_text(data) {
    //show the text connection information in the right sidebar
    _add_back_to_overview_button();
    var cd = data.connection_dict
    var fields = data.connection_dict.original.serialized.fields
    var original= data.connection_dict.original
    var original_author = cd.original_author;
    var original_title= cd.original_title;
    var original_genre= cd.original.genre;
    // console.log('righ sidebar connection view',data)
    _add_connection_instance_info(original,true)
    _add_other_connection_info(cd.translations, 'Translations')
    _add_other_connection_info(cd.reviews, 'Reviews')
}

function show_right_sidebar(index) {
	//show sidebar with entries from selected location
	clear_right_sidebar();
	if (markers.clustered_marker_indices.includes(index)) {
		var elements = markers.clustered_marker_dict[index].elements;
		for (let i=0; i < elements.length; i++) {
			var el= elements[i];
			var information = markers.d[el.options.index];
			show_city(information)
		}
        info.right_sidebar_elements = markers.clustered_marker_dict[index].elements;
	} else {
        info.right_sidebar_elements = false;
		var information =markers.d[index];
		show_city(information)
	}
    info.right_sidebar_active = true;
    info.right_sidebar_index = index;
    console.log('rsi',info.right_sidebar_index)
}

function update_right_sidebar() {
    if (info.right_sidebar_active === false || info.right_sidebar_index === false) {
        // if right sidebar is not active do not update it
        console.log('right sidebar not active, doing nothing')
        return;
     }
    if (info.right_sidebar_elements === false) {
        // only one city linked to this marker showing info related to that city
        console.log('updating sidebar')
        show_right_sidebar(info.right_sidebar_index);    
        return;
    }
    // multiple cities linked to marker, showing info related to each city
    //console.log(info.right_sidebar_elements)
    var indices = []
    for (let i = 0; i < info.right_sidebar_elements.length; i++) {
        var el = info.right_sidebar_elements[i]
        if (markers.clustered_marker_indices.includes(el.options.index)) {
            show_right_sidebar(el.options.index) 
            return
        } else {
            indices.push(el.options.index)
        }
    }
    for (let i = 0; i < indices.length; i++) {
        var index = indices[i];
        if ( markers.d[index] != undefined && markers.d[index].count > 0) { 
            show_right_sidebar(index);
            return;
        }
    }
    console.log('could not update right sidebar, closing')
    close_right_sidebar();
}
        

function toggle_sidebar_category(element) {
	//hide reveal category items (e.g. Text) from sidebar
	var dlinks = document.getElementById(element.dataset.links_id);
	if (dlinks.style.display == "") {
		element.style.color = element.data_color_inactive;//"grey";
		dlinks.style.display = "none";
	} else {
		element.style.color = element.data_color_active;//"#2f3030";
		dlinks.style.display = "";
	}
}

function show_info(index) {
	// shows general information (number of linked instances) 
	// about a location at the top of the screen
    console.log(index);
	var label = document.getElementById('city_label');
	if (markers.clustered_marker_indices.includes(index)) {
		//multiple locations are clustered into 1 marker
		var elements = markers.clustered_marker_dict[index].elements; var html = ''
		for (let i=0; i < elements.length; i++) {
			var el= elements[i];
			var information = markers.d[el.options.index];
			html += information.name
			html += '<small> (' + information.count + ')</small>';
			if (html.length > 140) {
				html += '<small> [...] + ' + (elements.length - 1 - i) 
                html += ' locations'
				break
			}
			if (i != elements.length -1) { html += ', '; }
		}
	} else {
        if (info.connection_view) 
            { var information = markers.connection_d[index]; }
		else { var information =markers.d[index]; }
		var html = information.name;
		html += '<small> (' + information.count + ' entries) ';
		for (const x of information.model_names) {
			if (x) { html += x.toLowerCase() + ' '}
		}
		html += '</small>'
	}
	label.innerHTML = html
}


markers.update_markers(markers.active_markers);


// mymap.on('zoomend', function() {
map_info.map.on('zoomend', function() {
	// update the clustering after zooming in or out
	console.log('zoomed')
    if (info.connection_view) {var marker_types = 'connection_view'}
    else {var marker_types = 'overview'}
    var markers = markers.layerDict[marker_types];
	markers.update_markers(markers, map_info.map);
});

open_left_sidebar();

// ---- filtering ----

function count_array_overlap(a1,a2) {
	//count the overlapping items from array 2 in array 1
	var n = 0;
	for (let i = 0; i < a2.length; i ++) {
		var x = a2[i];
		if (a1.includes(x)) { n++; }
	}
	return n
}

function make_ids_omiting_one_category(category) {
	var temp = [];
	var category_names = Object.keys(info.id_dict);
	for (let i=0;i<category_names.lenght;i++) {
		var name = category_names[i];	
		if (name == 'all' || category == name) {continue;}
		var identifiers = get_ids_from_selected_filters_in_category(name);
		if (identifiers.length == 0) { continue; }
		temp.push(identifiers);
	}
	if (temp.length == 0) { var ids = info.id_dict['all'];}
	else if (temp.length == 1) { var ids = Array.from(...temp); }
	else {ids = intersection(temp);}
	return ids
}

function count_instances(category_name, filter_name) {
	// count the number of active instances for a given category
	var identifiers = info.id_dict[category_name][filter_name];
	var active = count_array_overlap(info.active_ids, identifiers)
	var inactive = identifiers.length - active;
	var ids = make_ids_omiting_one_category(category_name);
	var filtered_inactive = count_array_overlap(ids,identifiers);
	return [active,inactive,filtered_inactive]
}

function update_count_dict() {
	//update the dictionary of counts to sets the number of visible instances
	//for each category in the filter sidebar
	var keys = Object.keys(info.filter_active_dict);
	var count = 0;
	for (let i = 0; i< keys.length; i++) {
		var key = keys[i];
		var [category_name,filter_name] = key.split(',');
		if (category_name && filter_name) {
			var[active, inactive,filtered_inactive] = count_instances(category_name,filter_name);
			info.count_dict[key] ={};
			info.count_dict[key]['active'] = active;
			info.count_dict[key]['inactive'] = inactive;
			info.count_dict[key]['filtered_inactive'] = filtered_inactive;
		}
	}
}

function remove_selected_filters_from_category(category_name) {
	//filters out all filters from a filter category from selected_filters
	var temp = []
	for (let i=0;i<info.selected_filters.length;i++) {
		var filter_name = info.selected_filters[i];
		if (filter_name.includes(category_name)) {
			continue
		}
		else { temp.push(filter_name) }
	}
	info.selected_filters = temp;
}

function set_filter_active_dict(active=NaN,inactive=NaN,category_name=NaN) {
	var d_keys = Object.keys(info.filter_active_dict);
	var active_count=0;
	var inactive_count=0;
	for (let i=0;i<d_keys.length;i++) {
		var key = d_keys[i];
		if (key.includes(active)) {
			info.filter_active_dict[key] = 'active';
		}
		else if (key.includes(inactive)) {
			info.filter_active_dict[key] = 'inactive';
		}
		// count the number of active filters in a category
		if (key.includes(category_name) && key != category_name) {
			if (info.filter_active_dict[key] == 'active') {active_count ++;}
			if (info.filter_active_dict[key] == 'inactive'){inactive_count ++;}
		}
	}
	//if there are no inactive filters in an category, the category is active
	if (inactive_count == 0) {
		info.filter_active_dict[category_name] = 'active';
		remove_selected_filters_from_category(category_name);
	}
	//if there are no active filters in an category, the category is active
	//(the last active filter was turned off, activating the whole category
	else if (active_count == 0) {
		set_filter_active_dict(category_name,NaN,category_name);
	}
}

function get_ids_from_selected_filters_in_category(category) {
	//get all ids from selected filters in a category
	var category_ids = [];
	for (let i=0;i<info.selected_filters.length;i++) {
		var name = info.selected_filters[i];
		var [category_name,filter_name] = name.split(',');
		if (category != category_name) { continue; }
		var identifiers = info.id_dict[category_name][filter_name];
		category_ids.push(...identifiers);
	}
	return category_ids;
}

function update_active_ids() {
	var temp = [];
	if (info.selected_filters.length == 0) {
		info.active_ids = info.id_dict['all']
		return
	}
	var category_names = Object.keys(info.id_dict);
	for (let i = 0;i<category_names.length;i++){
		var name = category_names[i];
		if (name == 'all') { continue; }
		var identifiers = get_ids_from_selected_filters_in_category(name)
		if (identifiers.length == 0) { continue; }
		temp.push(identifiers);
		if (temp.length == 1) {info.active_ids = Array.from(...temp);}
		else {info.active_ids = intersection(temp);}
	}

}

function set_nentries() {
	var nentries = document.getElementById('nentries');
	nentries.innerText = '# Entries ' + info.active_ids.length;
}

function update_selected_filters(name) {
	// add a filtername to the selected filter array
	// the intersection of all instances linked to all selected filters
	// are the shown instances
	if (info.selected_filters.includes(name)) {
		info.selected_filters.splice(info.selected_filters.indexOf(name),1);
	}
	else { info.selected_filters.push(name);}
}

function toggle_filter(name) {
	//toggle a filter on or off (filtering or adding the associated instances)
	update_selected_filters(name)	
	var [category_name,filter_name] = name.split(',');
	if (info.filter_active_dict[category_name] == 'active') {
		//first filter term in a category is activated,
		//set all not other terms (ie not == name) to inactive
		set_filter_active_dict(name,  category_name, category_name);
	} else if (info.filter_active_dict[name] == 'active') {
		//this filter name is active and possibly one or more other filter names
		// in this category are active
		set_filter_active_dict(NaN,name,category_name);
	} else {
		//current filter name is inactive, activate it and linked instances
		set_filter_active_dict(name,NaN,category_name);
	}
	update_active_ids(); // set the active identifiers based on active filters
	update_count_dict(); // update the counts (besides the filters)
	update_filter_sidebar(); // show the filters and counts in the side bar
	set_nentries(); //update the entry counts
	update_info_count(); // update the count for each info in d 
    // update marker list to include only markers with active ids
	markers.update_active_markers();
	markers.update_markers(markers.active_markers); // show the markers with active ids
    update_right_sidebar(); // update entries shown in right sidebar
}


function toggle_filters_visible(name) {
	//toggle visibility of filter categories (ie set model filters to (in)visible)
	var filter_set = document.getElementById(name+'_filters');
	var filter_name = document.getElementById(name+'_filter');
	if (filter_set.style.display == '') {
		filter_set.style.display = 'none';
		filter_name.style.color = 'grey';
	} else {
		filter_set.style.display = '';
		filter_name.style.color = '#585e66';
	}
}

function update_filter_sidebar() {
	// update the filters in the sidebar to show the current state
	var fad_keys = Object.keys(info.filter_active_dict);
	for (let i=0;i<fad_keys.length;i++) {
		var key = fad_keys[i];
		var filter_btn = document.getElementById(key);
		if (!filter_btn) { continue; }
		var [category_name, filter_name] = key.split(',');
		var updated = false
		var active = info.count_dict[key]['active'];
		var inactive = info.count_dict[key]['inactive'];
		var filtered_inactive= info.count_dict[key]['filtered_inactive'];
		var t = filter_btn.innerText;
        var r;
		if (info.filter_active_dict[category_name] == 'active') {
			updated = true
			if (active == 0) {
				//hide filters with no active linked instances
				filter_btn.style.color='#bec4cf';
				r = '(0)';
				filter_btn.style.display='none';
			} else {
				r = '('+active+')';
				filter_btn.style.color = 'black'
				filter_btn.style.display = '';
			}
			filter_btn.innerText = t.replace(/\(.*\)/,r);
            t = filter_btn.innerText;
		}
		// mark slected filters with a dot
		if (info.selected_filters.includes(key)) {
			if (!t.includes('•')) { filter_btn.innerText = '•' + t;}
		} else {
			filter_btn.innerText = t.replace('•','');
		}
		if (updated) {continue;}

		var t = filter_btn.innerText;
		if (info.filter_active_dict[key] == 'active' && filter_btn) {
			r = '('+active+')';
			filter_btn.style.color='black';
		}
		if (info.filter_active_dict[key] == 'inactive' && filter_btn) {
			//this should take into account filters from other categories
			r = '('+filtered_inactive+')';
			filter_btn.style.color='#bec4cf';
			if (filtered_inactive == 0) {filter_btn.style.display='none';}
			else {filter_btn.style.display='';}
		}
		filter_btn.innerText=t.replace(/\(.*\)/,r);
	}

}


function filter_based_on_locationtype(identifiers,information) {
    if (identifiers.length == 0) { 
        // if there are no identifiers there is nothing to filter
        return identifiers
    }
    if (info.filter_active_dict['locationtype'] == 'active'){
        // if locationtype filter is not set to either setting or
        // publication do not filter
        return identifiers
    }
    var pk = (information.pk).toString();
    if (!Object.keys(info.locationtype_filter_dict).includes(pk)) {
        // if location identifier not in locationtype dict
        // there is nothing to filter
        return identifiers
    }
    // assume locationtype publication filter is active
    var name = 'publication';
    if (info.filter_active_dict['locationtype,setting'] == 'active') {
        // setting filter is active change name to 'setting'
        name = 'setting';
    }
    //get the identifiers linked to the current locationtype filter
    var lt_identifiers = info.locationtype_filter_dict[information.pk][name]
    // return the identifiers that are in both arrays
    identifiers = intersection([lt_identifiers,identifiers])
    return identifiers
}



function update_info_count() {
	//for each info in d (location information with linked instances)
	// check whether the identifiers are in active_ids and update the count
	for (let i=0;i<markers.d.length;i++) {
		var information = markers.d[i];
		var identifiers = information.identifiers
		identifiers = intersection([identifiers,info.active_ids])
        identifiers = filter_based_on_locationtype(identifiers,information)
		information.count = identifiers.length
	}
}



function update_category_headers() {
	var category_headers = document.getElementsByClassName('category-header');
	for (let i=0;i<category_headers.length;i++) {
		var category_header = category_headers[i];
		var ids = category_header.getAttribute('data-identifiers').split(',');
		var count = intersection([ids,info.active_ids]).length;
		//console.log(category_header,ids,count);
		if (count > 0) {
			var t = category_header.innerHTML;
			category_header.style.display = '';
			category_header.innerHTML= t.replace(/\(.*\)/,'('+count+')');
		}
		else {category_header.style.display = 'none';}
	}
}


window.toggle_filter = toggle_filter;
window.on_marker_click = on_marker_click;
window.on_marker_hover = on_marker_hover;
window.map_info = map_info;
window.info = info;
window.markers = markers;

export {show_info, show_right_sidebar}
