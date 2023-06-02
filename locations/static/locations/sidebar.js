
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
    update_filter_sidebar(info) {
        update_filter_sidebar(info);
    }

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

export function update_filter_sidebar(info) {
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

