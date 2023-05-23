
function show_info(index) {
	// shows general information (number of linked instances) 
	// about a location at the top of the screen
    console.log(index);
	var label = document.getElementById('city_label');
	if (clustered_marker_indices.includes(index)) {
		//multiple locations are clustered into 1 marker
		var elements = clustered_marker_dict[index].elements;
		var html = ''
		for (let i=0; i < elements.length; i++) {
			var el= elements[i];
			var info = d[el.options.index];
			html += info.name
			html += '<small> (' + info.count + ')</small>';
			if (html.length > 140) {
				html += '<small> [...] + ' + (elements.length - 1 - i) 
                html += ' locations'
				break
			}
			if (i != elements.length -1) { html += ', '; }
		}
	} else {
        if (connection_view) { var info = connection_d[index]; }
		else { var info =d[index]; }
		var html = info.name;
		html += '<small> (' + info.count + ' entries) ';
		for (const x of info.model_names) {
			if (x) { html += x.toLowerCase() + ' '}
		}
		html += '</small>'
	}
	label.innerHTML = html
}
