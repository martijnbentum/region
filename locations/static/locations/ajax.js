/*
async function get_instance(instance_id,instance_category) {
	//get information of a single instance via ajax call
	//currently not used
	var path = '/locations/ajax_instance/'
	path += instance_category.replaceAll('_','/') + '/'
	path += instance_id	
	const response = await fetch(path); 
	const data = await response.json()
}
*/

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
    info.markers.hide_markers(info.markers.layerDict['overview']);
    sidebar.close_left_sidebar();
    sidebar.clear_right_sidebar(info);
    info.markers.connection_d = Object.values(data.instances);
    for (i = 0; i<info.markers.connection_d.length; i++) {
            console.log(info.markers.connection_d[i], i, 1111)
            info.markers.make_circle_marker(info.markers.connection_d[i],
                i,'connection_view')
    }
    info.markers.update_markers(info.markers.layerDict['connection_view'])
    console.log(info.markers.clustered_marker_dict,
        info.markers.clustered_marker_indices,'cmd,cmi');
    var group = new L.featureGroup(info.markers.layerDict['connection_view'])
    info.map_info.map.fitBounds(group.getBounds().pad(.1))
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
