import {Map_info} from './map_info.js'
import {Markers} from './marker.js'


var id_dict = JSON.parse(document.getElementById('id-dict').textContent);
var temp = document.getElementById('filter-active-dict').textContent;
// linking filters 'gender,male' to state 'active' or 'inactive'
var filter_active_dict= JSON.parse(temp);
var temp = document.getElementById('locationtype_filter_dict').textContent;
// linking location id (153) to setting / publication set of identifiers 
var locationtype_filter_dict= JSON.parse(temp);
// list of identifiers that are active
var active_ids = id_dict['all']
var selected_filters = [];
var count_dict = {};

var right_sidebar_active = false;
var right_sidebar_index = false;
var right_sidebar_elements = false;
var right_sidebar_category_counts = {};

var entries = [];

//location_type unused??
var location_type = document.getElementById('location_type')
var connection_view = false;

class Info {
    constructor() {
        this.id_dict = id_dict;
        // linking filters 'gender,male' to state 'active' or 'inactive'
        this.filter_active_dict = filter_active_dict;
        // linking location id (153) to setting / publication set of identifiers 
        this.locationtype_filter_dict = locationtype_filter_dict;
        this.active_ids = id_dict['all'];
        // list of selected filters
        this.selected_filters = [];
        // linker filters 'gender,male' to active and inactive counts
        this.count_dict = {};
        this.right_sidebar_active = false;
        this.right_sidebar_index = false;
        this.right_sidebar_elements = false;
        this.right_sidebar_category_counts = {};
        this.entries = []
        this.location_type = location_type;
        this.connection_view = false;
        this.map_info = new Map_info();
        this.markers = new Markers(this.map_info);
    }

}

export {Info}
