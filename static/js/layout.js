$(document).ready(function(){
	$("#search-bar").submit(function(event) {
	let query = $("#search-bar").serialize();
	alert(query);
	event.preventDefault();
	// const host = window.location.hostname;
	// let url = 'host + '/search/' query';
	let url = window.location.host;
	$.get(url + "/search?" + query);
	
	});
});