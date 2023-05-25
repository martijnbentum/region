//module to handle creation and 'on' methods (on_click, on_hover etc)
import {
    open_right_sidebar
} from './sidebar.js';

import {cluster, sort_on_x} from './cluster_rf.js';

import {
    show_info,
	show_right_sidebar,
    } from './map_rf.js'
    

var d= JSON.parse(document.getElementById('d').textContent);
var d = Object.values(d)




class Markers {
    constructor(map_info) {
        this.map_info = map_info;
        this.last_clicked_marker = false;
        this.last_activated = false;
        this.last_deactivated = false;
        this.marker_color = '#4287f5'
        this.highlight_color = "#e6da09";
        this.click_color = "#fc0352";
        this.clustered_markers = [];
        this.clustered_marker_indices = [];
        this.clustered_marker_dict = {};
        this.names = 'overview,connection_view'.split(',');
        this.layerDict = {}
        this.d = d;
        this.connection_d = false;
        this._make_overview_markers();
        
    }

    _make_layers() {
        for (var i = 0; i<this.names.length; i++) {
            this.layerDict[this.names[i]] = [];
        }
    }

    _make_overview_markers() {
        this._make_layers();
        for (i = 0; i<d.length; i++) {
            this.make_circle_marker(d[i],i,'overview');
        }
        this.active_markers = [...this.layerDict['overview']];
    }

    make_circle_marker(loc,i, layer ) {
        //create a marker a circle
        var latlng = loc2latlng(loc);
        if (latlng == false) { return false;}
        name = loc.name
        var marker=L.circleMarker(latlng,{color:this.marker_color,weight:2,
            fillOpacity:0.3,
            className:loc.name, index:i,visible:'active'})
        marker.markers = this;
        var radius = 4;
        marker.setRadius(radius)
        add_marker_behavior(marker);
        this.layerDict[layer].push(marker)
    }

    update_markers(markers) {
        // show markers on map;
        //apply clustering to markers (cluster overlapping markers together
        //filter out markers without any active ids
        this.show_markers(markers, true);
        markers.sort(sort_on_x);
        [this.clustered_marker_dict, this.clustered_marker_indices] = cluster(markers)
        this.show_markers(markers, false);
    }

    update_active_markers(layer = 'overview'){
        //filter out info in d (location information with linked instances)
        // with a count of 0
        var markers = this.layerDict[layer];
        this.active_markers= []
        for (let i=0; i<markers.length;i++) {
            var marker = markers[i];
            if (this.d[marker.options.index].count > 0)
                // check if the marker info object has any active identifiers
                this.active_markers.push(marker);
        }
        this.active_markers.sort(sort_on_x);
    }

    show_markers(markers, make_point) {
        //var controlLayers;
        this.hide_markers(this.layerDict['overview']);
        this.hide_markers(this.layerDict['connection_view']);
        for (i = 0; i<markers.length; i++) {
            var marker = markers[i];
            var marker_index = marker.options.index;
            if (make_point) {
                marker.addTo(this.map_info.map);
            } else if (this.clustered_marker_indices.includes(marker_index)) {
                if (this.clustered_marker_dict[marker.options.index].plotted) {
                    continue;
                }
                let ce = this.clustered_marker_dict[marker_index].center_element;
                ce.addTo(this.map_info.map)
                this.clustered_marker_dict[marker.options.index].plotted = true;
            } else {
                // marker.addTo(mymap);
                marker.addTo(this.map_info.map)
            }
        }
    }

    hide_markers(markers) {
        //remove markers from map
        for (i = 0; i<markers.length; i++) {
            var marker = markers[i];
            marker.remove();
        }
    }

    activate_marker(marker) {
        //change the color of a marker to highlight when hovered
        if (marker == this.last_clicked_marker) { return false}
        try {marker.setStyle({fillColor:highlight_color, color:highlight_color});}
        catch {marker._icon.innerHTML = html_highlight_icon;}
        this.last_activated = marker;
    }
        
    deactivate_marker(marker) {
        //change the color of a marker to default when hovered
        if (marker == this.last_clicked_marker) { return false}
        if (this.last_activated == false) { return false }
        try {marker.setStyle(
            {fillColor:this.marker_color,color:this.marker_color});
        }
        catch {marker._icon.innerHTML = html_icon;}
        this.last_deactivated = marker;
    }

    set_marker_clicked(marker) {
        // change color of marker to clicked color
        this.set_marker_unclicked();
        try {marker.setStyle(
            {fillColor:this.click_color, color:this.click_color});
        }
        catch {marker._icon.innerHTML = html_highlight_icon;}
        this.last_clicked_marker = marker;
    }

    set_marker_unclicked() {
        // change color of marker to default color
        if (this.last_clicked_marker == false) { return false }
        var marker = this.last_clicked_marker;
        try {marker.setStyle(
            {fillColor:this.marker_color,color:this.marker_color});
        }
        catch {marker._icon.innerHTML = html_icon;}
        this.last_clicked_marker = false
    }


}




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
	// adds marker behavior for different map marker events
	marker.on('mouseover',on_marker_hover)
	marker.on('mouseout',on_marker_leave)
	marker.on('click',on_marker_click)
}

function on_marker_hover(e) {
	//show info in top bar and change color of an element on the map when hovered
    var markers = this.markers;
	markers.deactivate_marker(markers.last_activated);
	markers.activate_marker(this);
    console.log(this,'this marker');
	show_info(this.options.index);
}

function on_marker_leave(e) {
	//nothing to do now
}

function on_marker_click(e) {
	// opens right sidebar (if closed) removes old elements (if present) 
	// shows instances linked to location in sidebar
	var s = this.options.className;
    var markers = this.markers;
    console.log(markers);
	markers.set_marker_clicked(this)
	show_right_sidebar(this.options.index);
	open_right_sidebar();
}










export {
    on_marker_click,
    on_marker_hover,
    Markers
}
