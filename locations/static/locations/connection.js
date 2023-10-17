var mymap = L.map('mapid').setView([52.0055328,4.67565177],5);
var attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">'
attribution += 'OpenStreetMap contributors &copy; '
attribution += '<a href="https://carto.com/attribution">CARTO</a>'
const tileUrl = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'
const tiles = L.tileLayer(tileUrl,{attribution});
tiles.addTo(mymap);


var instances = JSON.parse(document.getElementById('instances').textContent);
var connection_dict= JSON.parse(document.getElementById('connection_dict').textContent);
var instance= JSON.parse(document.getElementById('instance').textContent);
var instance= JSON.parse(instance)[0];


console.log('instances');
console.log(instances);
console.log('connection_dict');
console.log(connection_dict);
console.log('instance');
console.log(instance);

var title = document.getElementById('title');
title.innerHTML = connection_dict.original_title;

var author = document.getElementById('author');
author.textContent= connection_dict.original_author;
