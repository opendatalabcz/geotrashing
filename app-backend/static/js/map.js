const LATLNG_API_URL = document.currentScript.getAttribute('latlng_url'); 
const STATUS_API_URL = document.currentScript.getAttribute('status_url');  


function json_to_table(column_names, rows){
    var columns_html = "\t<tr>\n"
    column_names.forEach(e => {
        columns_html +=  `\t\t<th> ${e} </th> \n`;
    });
    columns_html += "\t</tr>\n"

    rows_html = "" 
    rows.forEach(row => {
        row_html = "\t<tr>\n"
        row.forEach(e => {
            row_html += `\t\t<td> ${e} </td>\n`
        })
        row_html += "\t</tr>\n"
        rows_html +=  row_html
    });
    return `<table>
${columns_html}
${rows_html}
</table>`
}


function click_on(map, e, point, xy) {
    get_url = `${STATUS_API_URL}?lat=${point[0]}&lon=${point[1]}`
    jQuery.getJSON(get_url, function(data){ 
        var content
        if (data.result.length == 0) {
           content = (`<h5>Žádné informace za posledních 8 hodin.<\h5>`)
        }
        else{
            content = json_to_table(data.column_names, data.result) 
        } 
        L.popup()
            .setLatLng(point)
            .setContent(content) 
            .openOn(map);
     }) 
}


function add_to_map(map, latLng) {
    L.glify.points({
        map: map,
        data: Array.from(latLng),
        opacity: 1,
        size: 15,
        color: 'black',
        click: function(e, point, xy) {
            click_on(map, e, point, xy)
        }})
}


//PRAGUE BOUNDS
var corner1 = [50.2276294, 14.1911097]
var corner2 = [49.9584772, 14.6573419]
var bounds = L.latLngBounds(corner1, corner2);

var minZoom = 11;
var maxZoom = 17;

var mymap = L.map('map',{ 
    maxBounds: bounds, 
    maxZoom: maxZoom,
    minZoom: minZoom,
    preferCanvas: true}).setView([50.0835494, 14.4341414], 12);


L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: maxZoom,
    minZoom: minZoom,
    bounds: bounds,
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' ,
    id: 'Open StreepMap'
}).addTo(mymap);


jQuery.getJSON(LATLNG_API_URL, function(latlng_json){
    add_to_map(mymap, latlng_json)
})