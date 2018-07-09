#!flask/bin/python

def gen_kml(nlat,nlon):
	return """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>KmlFile</name>
    <Placemark>
      <name>Google West Campus 1</name>
      <Point>
        <coordinates>-122.0914977709329,37.42390182131783,0</coordinates>
      </Point>
    </Placemark>
    <Placemark>
      <name>Google West Campus 2</name>
      <Point>
        <coordinates>-122.0926995893311,37.42419403634421,0</coordinates>
      </Point>
    </Placemark>
    <Placemark>
      <name>Google West Campus 3</name>
      <Point>
        <coordinates>-122.0922532985281,37.42301710721216,0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>
"""

def gen_html(nlat,nlon):
	result="""
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>KML Click Capture Sample</title>
    <style>
      html, body {
        height: 470px;
        padding: 0;
        margin: 0;
        }
      #map {
       height: 460px;
       width: 300px;
       overflow: hidden;
       float: left;
       border: thin solid #333;
       }
      #capture {
       height: 460px;
       width: 580px;
       overflow: hidden;
       float: left;
       background-color: #ECECFB;
       border: thin solid #333;
       border-left: none;
       }
    </style>
  </head>
  <body>
    <div id="map"></div>
    <div id="capture"></div>
    <script>
      var map;
//      var src = 'https://drive.google.com/open?id=1yaYxBXMb3lF06clxBcfjNdjwbbmfBr8a';
//      var src = 'http://192.168.0.210:5000/spot/api/v1.0/map.kml';
      var src = 'https://github.com/shramov/leaflet-plugins/blob/master/examples/KML_Samples.kml';
//      var src = 'https://developers.google.com/maps/documentation/javascript/examples/kml/westcampus.kml'; 

      function initMap() {
        map = new google.maps.Map(document.getElementById('map'), {
          center: new google.maps.LatLng(""" + str(nlat) + "," + str(nlon) + """),
          zoom: 2,
          mapTypeId: 'terrain'
        });

        var kmlLayer = new google.maps.KmlLayer({
	  url: src,
          suppressInfoWindows: true,
          preserveViewport: false,
          map: map
        });
	kmlLayer.setMap(map);
        kmlLayer.addListener('click', function(event) {
          var content = event.featureData.infoWindowHtml;
          var testimonial = document.getElementById('capture');
          testimonial.innerHTML = content;
        });
      }
    </script>
    <script async defer
    src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBnZpQt34CbqONbKVS4S1DUmYFlTUBkX4Q&callback=initMap">
    </script>
  </body>
</html>"""
	return result


