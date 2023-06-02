import {update_right_sidebar} from './map_rf.js';
import {intersection} from './utils.js';
import {update_filter_sidebar} from './sidebar.js';

function count_array_overlap(a1,a2) {
	//count the overlapping items from array 2 in array 1
	var n = 0;
	for (let i = 0; i < a2.length; i ++) {
		var x = a2[i];
		if (a1.includes(x)) { n++; }
	}
	return n
}

function make_ids_omiting_one_category(category, info) {
	var temp = [];
	var category_names = Object.keys(info.id_dict);
	for (let i=0;i<category_names.lenght;i++) {
		var name = category_names[i];	
		if (name == 'all' || category == name) {continue;}
		var identifiers = get_ids_from_selected_filters_in_category(name,info);
		if (identifiers.length == 0) { continue; }
		temp.push(identifiers);
	}
	if (temp.length == 0) { var ids = info.id_dict['all'];}
	else if (temp.length == 1) { var ids = Array.from(...temp); }
	else {ids = intersection(temp);}
	return ids
}

function count_instances(category_name, filter_name, info) {
	// count the number of active instances for a given category
	var identifiers = info.id_dict[category_name][filter_name];
	var active = count_array_overlap(info.active_ids, identifiers)
	var inactive = identifiers.length - active;
	var ids = make_ids_omiting_one_category(category_name,info);
	var filtered_inactive = count_array_overlap(ids,identifiers);
	return [active,inactive,filtered_inactive]
}

function update_count_dict(info) {
	//update the dictionary of counts to sets the number of visible instances
	//for each category in the filter sidebar
	var keys = Object.keys(info.filter_active_dict);
	var count = 0;
	for (let i = 0; i< keys.length; i++) {
		var key = keys[i];
		var [category_name,filter_name] = key.split(',');
		if (category_name && filter_name) {
			var[active, inactive,filtered_inactive] = count_instances(
                category_name,filter_name, info);
			info.count_dict[key] ={};
			info.count_dict[key]['active'] = active;
			info.count_dict[key]['inactive'] = inactive;
			info.count_dict[key]['filtered_inactive'] = filtered_inactive;
		}
	}
}

function remove_selected_filters_from_category(category_name, info) {
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

function set_filter_active_dict(info,active=NaN,inactive=NaN,category_name=NaN) {
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
		remove_selected_filters_from_category(category_name,info);
	}
	//if there are no active filters in an category, the category is active
	//(the last active filter was turned off, activating the whole category
	else if (active_count == 0) {
		set_filter_active_dict(info,category_name,NaN,category_name);
	}
}

function get_ids_from_selected_filters_in_category(category, info) {
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

function update_active_ids(info) {
	var temp = [];
	if (info.selected_filters.length == 0) {
		info.active_ids = info.id_dict['all']
		return
	}
	var category_names = Object.keys(info.id_dict);
	for (let i = 0;i<category_names.length;i++){
		var name = category_names[i];
		if (name == 'all') { continue; }
		var identifiers = get_ids_from_selected_filters_in_category(name,info)
		if (identifiers.length == 0) { continue; }
		temp.push(identifiers);
		if (temp.length == 1) {info.active_ids = Array.from(...temp);}
		else {info.active_ids = intersection(temp);}
	}

}

function set_nentries(info) {
	var nentries = document.getElementById('nentries');
	nentries.innerText = '# Entries ' + info.active_ids.length;
}

function update_selected_filters(name,info) {
	// add a filtername to the selected filter array
	// the intersection of all instances linked to all selected filters
	// are the shown instances
	if (info.selected_filters.includes(name)) {
		info.selected_filters.splice(info.selected_filters.indexOf(name),1);
	}
	else { info.selected_filters.push(name);}
}

function filter_toggle_filter(name, info) {
	//toggle a filter on or off (filtering or adding the associated instances)
	update_selected_filters(name,info)
	var [category_name,filter_name] = name.split(',');
	if (info.filter_active_dict[category_name] == 'active') {
		//first filter term in a category is activated,
		//set all not other terms (ie not == name) to inactive
		set_filter_active_dict(info,name,  category_name, category_name);
	} else if (info.filter_active_dict[name] == 'active') {
		//this filter name is active and possibly one or more other filter names
		// in this category are active
		set_filter_active_dict(info,NaN,name,category_name);
	} else {
		//current filter name is inactive, activate it and linked instances
		set_filter_active_dict(info,name,NaN,category_name);
	}
    // set the active identifiers based on active filters
	update_active_ids(info); 
    // update the counts (besides the filters)
	update_count_dict(info); 
	update_filter_sidebar(info); // show the filters and counts in the side bar
	set_nentries(info); //update the entry counts
	update_info_count(info); // update the count for each info in d 
    // update marker list to include only markers with active ids
	info.markers.update_active_markers();
	info.markers.update_markers(info.markers.active_markers); // show the markers with active ids
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

function filter_based_on_locationtype(identifiers,information, info) {
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

function update_info_count(info) {
	//for each info in d (location information with linked instances)
	// check whether the identifiers are in active_ids and update the count
	for (let i=0;i<info.markers.d.length;i++) {
		var information = info.markers.d[i];
		var identifiers = information.identifiers
		identifiers = intersection([identifiers,info.active_ids])
        identifiers = filter_based_on_locationtype(identifiers,information,info)
		information.count = identifiers.length
	}
}


export {filter_toggle_filter}
