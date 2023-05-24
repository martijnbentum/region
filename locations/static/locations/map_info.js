// store objects with map related info, map is a leaflet object

var attribution= '&copy; <a href="https://www.openstreetmap.org/copyright">'
attribution+= 'OpenStreetMap contributors &copy; '
attribution+= '<a href="https://carto.com/attribution">CARTO</a>'
const tile_url = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'
const tiles = L.tileLayer(tile_url,{attribution});
var layer_names = 'overview,connection_view'.split(',');

class Map_info {
    constructor() {
        this.set_info()
        this._set_layers()
    } 

    set_info() {
        this.attribution = attribution;
        this.tile_url = tile_url;
        this.tiles = tiles;
        this.map = L.map('mapid').setView([52.0055328,4.67565177],5);
        tiles.addTo(this.map);
    }

    _set_layers() {
        this.layer_names = layer_names;
        this.layers = {};
        for (var i = 0; i< this.layer_names.length; i ++) {
            this.layers[this.layer_names[i]] = []
        }
    }

    add_marker(marker, layer_name) {
        this.layers[layer_name].push(marker);
    }

    add_markers(markers, layer_name) {
        for (i = 0; i<markers.length; i++) {
            let marker = markers[i];
            this.layers[layer_name].push(marker);
        }
    }
}

export {Map_info}
