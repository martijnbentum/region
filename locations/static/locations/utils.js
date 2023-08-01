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

function count_active_identifiers(identifiers) {
    var count = 0;
    for (const identifier of identifiers) {
        if (info.active_ids.includes(identifier)) { count += 1;}
    }
    return count;
}

function intersection(array_of_arrays) {
	// returns an array of items that occur in all arrays
	var data = array_of_arrays;
	var result = data.reduce( (a,b) => a.filter( c => b.includes(c) ) );
	return result
}



export {
    pks_and_category_to_identifiers, 
    intersection,
    count_active_identifiers,
};
