
// leaflet map setup
var latitude= JSON.parse(document.getElementById('latitude').textContent);
var longitude= JSON.parse(document.getElementById('longitude').textContent);
console.log(latitude,longitude)
var mymap = L.map('mapid').setView([latitude,longitude],5);
var attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">'
attribution += 'OpenStreetMap contributors &copy; '
attribution += '<a href="https://carto.com/attribution">CARTO</a>'
const tileUrl = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'
const tiles = L.tileLayer(tileUrl,{attribution});
tiles.addTo(mymap);
var marker = L.marker([latitude, longitude]).addTo(mymap)

