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

