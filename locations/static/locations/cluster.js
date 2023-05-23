function find_center(elements) {
	// find the center of a set of leaflet elements
	var x = 0;
	var y = 0;
	for (let i = 0; i<elements.length; i++) {
		var el = elements[i];
		x += el._point['x']
		y += el._point['y']
	}
	return {'x': parseInt(x / elements.length) , 'y': parseInt(y / elements.length)}
}

function find_center_element(elements) {
	// find the element closest to the center of the set of leaflet elements
	var center = find_center(elements)
	var center_point = L.point(center);
	var smallest_distance = 800;
	var index = 0;
	for (let i = 0; i<elements.length; i++) {
		var el = elements[i];
		var distance = el._point.distanceTo(center_point);	
		if (distance < smallest_distance) {
			smallest_distance = distance;
			index = i;
		}
	}
	return elements[index]
}

function sort_on_x(a,b) {
	// sort on the x dimension of leaflet elements
	return a._point['x'] - b._point['x']
}

function sort_on_y(a,b) {
	// sort on the y dimension of leaflet elements
	return a._point['y'] - b._point['y']
}

function filter_1d_distance(arr,index, dimension = 'x', radius = 4) {
	//assumes arr is sorted on specified dimension
	var max_distance = radius * 2;
	var number = arr[index]._point[dimension]
	var output = []
	for (let i = 0; i<arr.length; i++) {
		var el = arr[i]
		var delta =  el._point[dimension] - number 
		if ( delta < 0 && Math.abs(delta) > max_distance ) { continue; }
		else if (Math.abs(delta) <= max_distance) { output.push(el); }
		else { break; }
	}
	return output
}

function filter_2d_distance(arr,index,radius=4) {
	// filter elements based on a maximum distance (i.e. 2*radius)
	// the leaflet distance function is used
	// the function assumes the array is sorted on the x dimension to do early stopping
	var max_distance = radius * 2;
	var output = []
	var reference_point = arr[index]._point;
	var number = reference_point['x']
	for (let i = 0; i<arr.length; i++) {
		var el = arr[i]
		var delta =  el._point['x'] - number 
		if ( delta < 0 && Math.abs(delta) > max_distance ) { continue; }
		else if (Math.abs(delta) <= max_distance) { 
			var distance =  el._point.distanceTo(reference_point)
			if (distance <= max_distance) { output.push(el); }
		}
		else { break; }
	}
	return output
}


function check_overlap_number_array(arr1,arr2) {
	// check whether an number array contains one or more identical numbers
	return arr1.some(number=> arr2.includes(number)) 
}

function make_array_unique(arr) {
	// remove non unique elements from an array
	return arr.filter((el,pos) => arr.indexOf(el) === pos);
}

function combine_overlapping_number_array(arr1,arr2) {
	//combine a number array with only unique elements
	var temp = arr1.concat(arr2);
	return make_array_unique(temp)
}

function _combine_number_arrays(number_arrays) {
	// recursive function that combines number arrays with one or more identical numbers
	// helper function of combine_ clusters
	var output = []
	var combined = 0;
	var skip_indices = []
	for (let i = 0; i < number_arrays.length; i++) {
		if (skip_indices.includes(i)) {continue}
		skip_indices.push(i)
		var na1 = number_arrays[i]
		var temp = [...na1];
		var add_to_output = true;
		for (let j = 0; j < number_arrays.length; j++) {
			if (skip_indices.includes(j)) {continue}
			var na2 = number_arrays[j];
			if (check_overlap_number_array(na1,na2)) {
				skip_indices.push(j)
				var temp = combine_overlapping_number_array(na1,na2)
				output.push(temp);
				combined++  
				add_to_output = false;
			}
		}
		if (add_to_output) { output.push(na1); }
	}
	if (combined > 0) {
		return _combine_number_arrays(output)
	}
	// there is nothing to combine the recursion break and the number array is returned
	return number_arrays
}

function _combine_clusters(clusters,cluster_dict) {
	//combines clusters when they contain one or more identical leaflet elements
	//helper function of cluster
	var combined_clusters = [];
	var indices= Object.values(cluster_dict)
	indices = _combine_number_arrays(indices)
	for (let i = 0; i < indices.length; i++) {
		var temp = []
		for (let j = 0; j < indices[i].length; j++) {
			var index = indices[i][j]
			elements = clusters[indices[i][j]]
			for (let k = 0; k < elements.length; k++) {
				var el = elements[k]
				if ( !(temp.includes(el)) ) { temp.push(el) }
			}
		}
		combined_clusters.push(temp)
	}
	return combined_clusters	
}

function cluster(arr, radius = 4) {
	// cluster leaflet elements that overlap based on a fixed radius size
	var clusters = []
	var clustered_element_indices = []
	var cluster_dict = {};
	for (let i = 0; i < arr.length; i++) {
		var o = filter_2d_distance(arr,i,radius=radius)
		if ( o.length > 1 ) { 
			clusters.push(o); 
			for (let j = 0; j < o.length; j++) {
				el = o[j]
				if ( !(clustered_element_indices.includes(el.options.index)) ) {
					clustered_element_indices.push(el.options.index)
				}
				if (! (el._leaflet_id in cluster_dict) ) {
					cluster_dict[el._leaflet_id] = [clusters.length - 1]
				} else {
					cluster_dict[el._leaflet_id].push(clusters.length - 1)
				}
			}
		}
	}
	clusters = _combine_clusters(clusters,cluster_dict);
	clustered_elements_dict = make_clustered_elements_dict(clusters);
	return [clustered_elements_dict, clustered_element_indices]
}

function make_clustered_elements_dict(clustered_elements) {
	clustered_elements_dict= {}
	for (var i = 0; i< clustered_elements.length; i++) {
		var d = {}
		var elements = clustered_elements[i];
		d['elements'] = elements;
		d['center_element'] = find_center_element(elements);
		d['plotted'] = false;
		for (var j = 0; j < elements.length; j++) {
			el = elements[j]
			clustered_elements_dict[el.options.index] = d
		}
	}
	return clustered_elements_dict
}


function time_cluster(arr) {
	console.time('do something')
	cluster(arr);
	console.timeEnd('do something')
}


var a = [1,2,3];
var b = [3,4,5];
var d = [17,8,9];
var e = [117,80,19];
var f = [a,b,d,e];

//comment

