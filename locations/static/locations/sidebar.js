import {
    pks_and_category_to_identifiers,
    count_active_identifiers
} from './utils.js';

import {
    get_instances,
} from './map_rf.js';

export class Sidebar {
    constructor() {
    }

    open_left_sidebar() {
        open_left_sidebar();
    }
    open_right_sidebar() {
        open_right_sidebar();
    }
    close_left_sidebar() {
        close_left_sidebar();
    }
    close_right_sidebar() {
        close_right_sidebar();
    }
    update_filter_sidebar() {
        update_filter_sidebar();
    }
    clear_right_sidebar() {
        clear_right_sidebar();
    }
    show_right_sidebar(index) { 
        show_right_sidebar(index)
    }
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
	var sidebar_window= document.getElementById('right_sidebar_content');
	var city_div =document.createElement("d");
	sidebar_window.appendChild(city_div)
	city_div.id = information.pk + "-links";
	info.entries.push(city_div)
	for (const [key, instance_ids] of Object.entries(information)) {
		if ('count,model_names,name,gps,pk,identifiers'.split(',').includes(key)){
		} else {
			show_category(instance_ids, key, city_div );
		}
	}
}

function show_city(information) {
	//show all information linked to specific location
    console.log(information)
	var sidebar_window= document.getElementById('right_sidebar_content');
	var div =document.createElement("d");
	sidebar_window.appendChild(div);
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

export function show_right_sidebar(index) {
	//show sidebar with entries from selected location
	clear_right_sidebar();
    // var index = info.right_sidebar_index; 
	if (info.markers.clustered_marker_indices.includes(index)) {
		var elements = info.markers.clustered_marker_dict[index].elements;
		for (let i=0; i < elements.length; i++) {
			var el= elements[i];
			var information = info.markers.d[el.options.index];
			show_city(information);
		}
        info.right_sidebar_elements = info.markers.clustered_marker_dict[index].elements;
	} else {
        info.right_sidebar_elements = false;
        console.log(index,'index')
		var information =info.markers.d[index];
		show_city(information);
	}
    info.right_sidebar_active = true;
    info.right_sidebar_index = index;
    console.log('rsi',info.right_sidebar_index)
}

export function update_right_sidebar() {
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
        if (info.markers.clustered_marker_indices.includes(el.options.index)) {
            show_right_sidebar(el.options.index) 
            return
        } else {
            indices.push(el.options.index)
        }
    }
    for (let i = 0; i < indices.length; i++) {
        var index = indices[i];
        if ( info.markers.d[index] != undefined && info.markers.d[index].count > 0) { 
            show_right_sidebar(index);
            return;
        }
    }
    console.log('could not update right sidebar, closing')
    close_right_sidebar();
}

export function open_left_sidebar() {
	// open sidebar
	document.getElementById("left_sidebar").style.width = "180px";
	document.getElementById("content").style.marginLeft = "183px";
}

export function close_left_sidebar() {
	// close sidebar
	document.getElementById("left_sidebar").style.width = "0px";
	document.getElementById("content").style.marginLeft = "25px";
}

export function open_right_sidebar() {
	// open sidebar
	document.getElementById("right_sidebar").style.width = "400px";
	document.getElementById("content").style.marginRight = "403px";
	document.getElementById("search_div").style.marginRight = "353px";
}

export function close_right_sidebar() {
	// close sidebar
	document.getElementById("right_sidebar").style.width = "0px";
	document.getElementById("content").style.marginRight= "25px";
	document.getElementById("search_div").style.marginRight = "25px";
}


function clear_right_sidebar() {
    //remove old entries from sidebar
    var sidebar= document.getElementById('right_sidebar_content');
    for (const x of info.entries) {
        x.remove()
    }
    info.entries = [];
}

export function update_filter_sidebar() {
	// update the filters in the left sidebar to show the current state
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


