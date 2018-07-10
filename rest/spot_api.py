#!flask/bin/python

from flask import Flask, jsonify, abort, request, make_response, url_for, Response
import time
from flask_httpauth import HTTPBasicAuth

# import json
import psycopg2
import spot_db
import spot_kml
import uuid

import logging, logging.config, yaml
logging.config.dictConfig(yaml.load(open('logging.conf')))
logfl    = logging.getLogger('file')
logconsole = logging.getLogger('console')
logfl.debug("Debug FILE")
logconsole.debug("Debug CONSOLE")

app = Flask(__name__, static_url_path = "")
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'testuser':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
#    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 401)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog
    
@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

users = [
    {
        'id': "olga",
        'wallet': '0x12341q42134khjsagdf2345235',
        'created_at': '2017-01-02 00:02:03', 
    },
    {
        'id': "igor",
        'wallet': '0x12341q42134khjsagdf2345235',
        'created_at': '2017-01-03 00:02:03', 
    },
    {
        'id': "nastya",
        'wallet': '0x12341412134khjsagdf2345235',
        'created_at': '2017-11-04 00:02:03', 
    }
]

spots = [
   {
      "at": 1522890284.214637, 
      "deg": 126, 
      "loc": {
        "al": 0, 
        "lg": -117.7876202, 
        "lt": 33.66965465
      }, 
      "spot": [
        1, 
        4, 
        2
      ], 
      "uid": "daniel", 
      "uri": "http://spot.selfip.com:65000/spot/api/v1.0/spot?id=h2"
    }
]

def make_public_user(user):
    new_user = {}
    for field in user:
        if field == 'id':
            new_user['uri'] = url_for('create_user', id = user['id'], _external = True)
        else:
            if field == 'wallet':
                new_user['wallet'] = "hidden"
            else:
                new_user[field] = user[field]
    return new_user

def make_public_spot(spot):
    new_spot = {}
    for field in spot:
        if field == 'id':
            new_spot['uri'] = url_for('create_spot', id = spot['id'], _external = True)
        else:
            new_spot[field] = spot[field]
    return new_spot

@app.route('/spot/api/v1.0/users', methods = ['GET'])
@auth.login_required
def get_users():
    return jsonify( { 'users': map(make_public_user, users) } )

@app.route('/spot/api/v1.0/map', methods = ['GET'])
@auth.login_required
def get_map():
    mid = request.args.get('mid', None)
    pid = request.args.get('pid', None)
    lt = request.args.get('lt', None)
    lg = request.args.get('lg', None)
    logconsole.debug("running map with "+str(request.args)+" lt="+str(lt)+" lg="+str(lg)+" mid="+str(mid)+" pid="+str(pid))
    if lt == None and lg == None and mid == None and pid == None :
        abort(400)
    spot_db.openConn()
    coord_array = []	
    if pid != None: 
       coord_array=spot_db.getParkedSpots(pid)
       if coord_array != None and len(coord_array) > 0:
       	  lg=coord_array[0][0]	
       	  lt=coord_array[0][1]	
       logconsole.debug("determined parked lt="+str(lt)+" lg="+str(lg)+" for mid="+str(mid))
    else:
    	if mid != None: 
      	  coord_array=spot_db.getReportedSpots(mid)
       	  if coord_array != None and len(coord_array) > 0:
	    lg=coord_array[0][0]          
            lt=coord_array[0][1]  
      	  logconsole.debug("determined reported lt="+str(lt)+" lg="+str(lg)+" for mid="+str(mid))
    	else:
       	  coord_array=spot_db.getNearSpots(lt,lg)
    logconsole.debug("coords returned "+str(coord_array))
    ufilename = "maps/ag_"+uuid.uuid4().hex+".kml"
    spot_kml.gen_kml(coord_array, ufilename)
    html=spot_kml.gen_html(lt, lg, ufilename)
    resp = make_response(html, 200)
    spot_db.cur.close()
    spot_db.conn.close()
    resp.headers['Content-type'] = 'text/html'
    return resp

@app.route('/spot/api/v1.0/spots', methods = ['GET'])
@auth.login_required
def get_spots():
    sorted_spots=sorted(spots, key=lambda k: k['at'], reverse=True)
    return jsonify( { 'spots': map(make_public_spot, sorted_spots) } )

@app.route('/spot/api/v1.0/users/<string:user_id>', methods = ['GET'])
@auth.login_required
def get_user(user_id):
    user = filter(lambda t: t['id'] == user_id, users)
    if len(user) == 0:
        abort(404)
    return jsonify( { 'user': make_public_user(user[0]) } )

@app.route('/spot/api/v1.0/register', methods = ['POST'])
@auth.login_required
def create_user():
    logconsole.debug("register called with "+str(request.json))
    if not request.json or not 'id' in request.json:
        abort(400)
    user = {
        'id': request.json['id'],
        'wallet': '0x12341q42134khjsagdf2345235',
        'created_at': time.time(),
        'tokens': 20
    }
    users.append(user)
    spot_db.openConn()
    informer_id=spot_db.getUserID(request.json['id'])
    if ( informer_id is None ) :
       spot_db.newUser(request.json['id'])
       informer_id=spot_db.getUserID(request.json['id'])

    spot_db.cur.close()
    spot_db.conn.close()    
    logconsole.debug("registered user "+request.json['id']+" db key ="+informer_id)
    return jsonify( { 'user': make_public_user(user) } ), 201

@app.route('/spot/api/v1.0/spot', methods = ['POST'])
@auth.login_required
def create_spot():
    logconsole.debug("create_spot called with "+str(request.json))
    if not request.json or not 'uid' in request.json:
        abort(400)
    if not request.json or not 'loc' in request.json:
        abort(400)
    if not request.json or not 'spot' in request.json:
        abort(400)
    if not request.json or not 'deg' in request.json:
        abort(400)
    spot = {
        'id': "h2",
        'uid': request.json['uid'], 
        'loc': request.json['loc'],
        'spot' : request.json['spot'],
        'deg' : request.json['deg'],
        'at': time.time(),
        'ct': request.json['ct'],
    }
    spots.append(spot)
    spot_db.openConn()
    for spt in request.json['spot']:
    	rc = spot_db.insertSpot(request.json['uid'],int(round(time.time() * 1000)),request.json['deg'],request.json['loc']['al'],
            request.json['loc']['lg'],request.json['loc']['lt'],spt,request.json['ct'])
	if ( rc != 0 ):
		abort(rc) 

    spot_db.cur.close()
    spot_db.conn.close()    
    return jsonify( { 'spot': make_public_spot(spot) } ), 201

@app.route('/spot/api/v1.0/take', methods = ['POST'])
@auth.login_required
def take_spot():
    logconsole.debug("take_spot called with "+str(request.json))
    if not request.json or not 'uid' in request.json:
        abort(400)
    if not request.json or not 'ct' in request.json:
        abort(400)
    if not request.json or not 'sid' in request.json:
        abort(400)
    if not request.json or not 'loc' in request.json:
        abort(400)
    spot = {
        'uid': request.json['uid'], 
        'sid': request.json['sid'], 
        'loc': request.json['loc'],
        'at': time.time(),
        'ct': request.json['ct'],
    }
    spots.append(spot)
# 2018-05-08 02:57:27,299 - file - DEBUG - Take called with {u'loc': {u'lg': 6.7, u'lt': 3.4, u'al': 5.9}, u'ct': u'12121212121212', u'uid': u'igor', u'sid': u'jhgjhgjhgjhgjhgjhgjhg'}
    spot_db.openConn()
    rc = spot_db.updateSpot(request.json['uid'],request.json['sid'],int(round(time.time() * 1000)),request.json['ct'])
    if ( rc != 0 ):
        abort(rc)
    spot_db.cur.close()
    spot_db.conn.close()	
    return jsonify( { 'spot': make_public_spot(spot) } ), 201

@app.route('/spot/api/v1.0/park', methods = ['POST'])
@auth.login_required
def park_parked():
    logconsole.debug("park_parked called with "+str(request.json))
    if not request.json or not 'uid' in request.json:
        abort(400)
    if not request.json or not 'ct' in request.json:
        abort(400)
    if not request.json or not 'loc' in request.json:
        abort(400)
    if not request.json or not 'deg' in request.json:
        abort(400)
    spot = {
        'uid': request.json['uid'], 
        'loc': request.json['loc'],
        'at': time.time(),
        'ct': request.json['ct'],
    }
    spots.append(spot)
    spot_db.openConn()
    rc = spot_db.insertParked(request.json['uid'],int(round(time.time() * 1000)),request.json['deg'],request.json['loc']['al'],
       request.json['loc']['lg'],request.json['loc']['lt'],request.json['ct'])
    if ( rc != 0 ):
       abort(rc)

    spot_db.cur.close()
    spot_db.conn.close()
    return jsonify( { 'spot': make_public_spot(spot) } ), 201

@app.route('/spot/api/v1.0/locate', methods = ['POST'])
@auth.login_required
def get_locate():
    sorted_spots=sorted(spots, key=lambda k: k['at'], reverse=True)
    logconsole.debug("locate called with "+str(request.json))

    if not request.json or not 'loc' in request.json:
        abort(400)
    logconsole.debug("Locate called with "+str(request.json))
    spot_db.openConn()

    res=spot_db.locateSpot(request.json['loc']['lt'],request.json['loc']['lg'])
    logconsole.debug("Locate found in db "+str(res))
# Locate called with {u'loc': {u'lg': -117.71802732, u'lt': 33.58032164, u'al': 73}}
# Locate found in db ('c1a1defc-0d93-427c-b0d7-601e08d1637d', 0L, datetime.timedelta(660), 4.63180451482997, 33.58035109, -117.71799196)

    spot_db.cur.close()
    spot_db.conn.close()	
    gspots = [
       {
         "at": 1,
         "deg": 1,
	 "sid": res[0],
         "loc": {
           "al": 0,
           "lg": res[5],
           "lt": res[4]
         },
         "spot": [
           res[1],
         ],
        "uid": "igor",
        "uri": "http://spot.selfip.com:65000/spot/api/v1.0/spot?id=h2"
       }
    ]
    logconsole.debug("Locate constructed json response "+str(gspots))

    return jsonify( { 'spots': map(make_public_spot, gspots) } )

if __name__ == '__main__':
#    app.run(debug = True)

    app.run(host="0.0.0.0")
