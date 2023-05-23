//simple helper functions for the map functionality

function pk_and_category_to_identifier(pk,category) {
	//create an identifier string from a number and class and 
    //model name (ie. category)
	return category.toLowerCase() + '_' + pk
}

function pks_and_category_to_identifiers(pks,category) {
	//create an identifier string from a numbers and class and 
    //model name (ie. category)
	var identifiers = []
	for (let i=0;i<pks.length;i++) {
		var pk = pks[i];
		identifiers.push(pk_and_category_to_identifier(pk,category));
	}
	return identifiers
}

function intersection(array_of_arrays) {
	// returns an array of items that occur in all arrays
	var data = array_of_arrays;
	var result = data.reduce( (a,b) => a.filter( c => b.includes(c) ) );
	return result
}

function open_left_nav() {
	// open sidebar
	document.getElementById("left_sidebar").style.width = "180px";
	document.getElementById("content").style.marginLeft = "183px";
}

function close_left_nav() {
	// close sidebar
	document.getElementById("left_sidebar").style.width = "0px";
	document.getElementById("content").style.marginLeft = "25px";
}

function open_right_nav() {
	// open sidebar
	document.getElementById("right_sidebar").style.width = "400px";
	document.getElementById("content").style.marginRight = "403px";
	document.getElementById("search_div").style.marginRight = "353px";
}

function close_right_nav() {
	// close sidebar
	document.getElementById("right_sidebar").style.width = "0px";
	document.getElementById("content").style.marginRight= "25px";
	document.getElementById("search_div").style.marginRight = "25px";
}


export {
    pks_and_category_to_identifiers, 
    intersection,
    open_left_nav,
    open_right_nav,
    close_left_nav,
    close_right_nav,
};
