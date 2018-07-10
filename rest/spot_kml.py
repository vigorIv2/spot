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
        <link rel="stylesheet" href="http://unpkg.com/leaflet@1.3.1/dist/leaflet.css" />
        <script src="http://unpkg.com/leaflet@1.3.1/dist/leaflet.js"></script>
        <script src="/maps/layer/vector/KML.js"></script>
</head>
<body>
        <div style="width:100%; height:100%" id="map"></div>
        <script type='text/javascript'>
                var map = new L.Map('map', {center: new L.LatLng("""+str(nlat)+","+str(nlon)+"""), zoom: 7});
                var osm = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
                var track = new L.KML("/"""+ufn+"""", {async: true});
                track.on("loaded", function(e) {
                        map.fitBounds(e.target.getBounds());
                });
                map.addLayer(track);
                map.addLayer(osm);
                map.addControl(new L.Control.Layers({}, {'parking':track}));
        </script>
</body>
</html>"""
	return result


