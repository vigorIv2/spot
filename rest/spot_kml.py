#!flask/bin/python
# -*- coding: utf-8 -*-

import io 

def gen_kml(ca,ufn):
        with io.open(ufn, 'w', encoding='utf-8') as outfile:
		outfile.write(unicode("<?xml version=\"1.0\" ?>\n<kml>\n<Document>\n"))
		if ca != None:
			for row in ca:
				l="<Placemark><Point><coordinates>"+str(row[0])+","+str(row[1])+"</coordinates></Point></Placemark>\n"
            			outfile.write(unicode(l))
		outfile.write(unicode("</Document>\n</kml>\n"))

def gen_html(nlat,nlon,ufn):
	result="""<html>
<head>
        <title>Leaflet</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.3.4/dist/leaflet.css" integrity="sha512-puBpdR0798OZvTTbP4A8Ix/l+A4dHDD0DGqYW6RQ+9jxkRFclaxxQb/SJAWZfWAkuyeQUytO7+7N4QKrDh+drA=="
   crossorigin="" />
        <script src="https://unpkg.com/leaflet@1.3.4/dist/leaflet.js" integrity="sha512-nMMmRyTVoLYqjP9hrbed9S+FzjZHW5gY1TWCHA5ckwXZBadntCNs8kEqAWdrb9O7rxbCaA4lKTIWjDXZxflOcA=="
   crossorigin=""></script>
        <script src="/maps/layer/vector/KML.js"></script>
</head>
<body>
        <div style="width:100%; height:100%" id="map"></div>
        <script type='text/javascript'>
                var map = new L.Map('map', {center: new L.LatLng("""+str(nlat)+","+str(nlon)+"""), zoom: 17, dragging: !L.Browser.mobile });
                var osm = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
		L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    			attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox.streets',
    accessToken: 'pk.eyJ1IjoidmFzaWxjaGlrb3YiLCJhIjoiY2pvaHI5ajZoMDFhZzNxbjF5dnlwOWFycSJ9.1Xp8pzjy7Q8FzB_WTKic2A'
}).addTo(map);

                var track = new L.KML("/"""+ufn+"""", {async: true});
                track.on("loaded", function(e) {
                        map.fitBounds(e.target.getBounds());
                });
                map.addLayer(track);
		map.locate({setView: true, maxZoom: 16});
                map.addLayer(osm);
                map.addControl(new L.Control.Layers({}, {'parking':track}));
        </script>
</body>
</html>"""
	return result

def gen_empty_html():
	result="""<html>
<head>
        <title>No data points</title>
</head>
<body>
        <h3>Empty data set</h3>
</body>
</html>"""
	return result


