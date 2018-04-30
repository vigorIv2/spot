#!flask/bin/python

from flask import Flask, jsonify, abort, request, make_response, url_for
import time
from flask_httpauth import HTTPBasicAuth

import json
import psycopg2

def openConn():
	global conn
	global cur
	conn = psycopg2.connect(database="huhula", user="root", host="roachdb", port=26257)
	conn.set_session(autocommit=True)
	cur = conn.cursor()

def getUserID(user) :
	cur.execute("SELECT id FROM users WHERE userhash = '" + user + "'")
	return cur.fetchone()[0]

def insertSpot(informer,informed_at,azimuth,altitude,longitude,latitude,spot,client_at) :
	informer_id=getUserID("strix")
	cur.execute("INSERT INTO huhula.spots(informer_id,informed_at,azimuth,altitude,longitude,latitude,spot,client_at) values(%s,%s,%s,%s,%s,%s,%s,%s)",
            (informer_id,informed_at,azimuth,altitude,longitude,latitude,spot,client_at))


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
    if not request.json or not 'id' in request.json:
        abort(400)
    user = {
        'id': request.json['id'],
        'wallet': '0x12341q42134khjsagdf2345235',
        'created_at': time.time(),
        'tokens': 20
    }
    users.append(user)
    return jsonify( { 'user': make_public_user(user) } ), 201

@app.route('/spot/api/v1.0/spot', methods = ['POST'])
@auth.login_required
def create_spot():
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
    openConn()
    for spt in request.json['spot']:
    	insertSpot(request.json['uid'],int(round(time.time() * 1000)),request.json['deg'],request.json['loc']['al'],
            request.json['loc']['lg'],request.json['loc']['lt'],spt,request.json['ct'])

    cur.close()
    conn.close()    
    return jsonify( { 'spot': make_public_spot(spot) } ), 201

@app.route('/spot/api/v1.0/take', methods = ['POST'])
@auth.login_required
def take_spot():
    if not request.json or not 'uid' in request.json:
        abort(400)
    if not request.json or not 'loc' in request.json:
        abort(400)
    if not request.json or not 'spot' in request.json:
        abort(400)
    spot = {
        'id': "h2",
        'uid': request.json['uid'], 
        'loc': request.json['loc'],
        'spot' : request.json['spot'],
        'at': time.time(),
        'ct': request.json['ct'],
    }
    spots.append(spot)
    return jsonify( { 'spot': make_public_spot(spot) } ), 201

@app.route('/spot/api/v1.0/locate', methods = ['POST'])
@auth.login_required
def get_locate():
    sorted_spots=sorted(spots, key=lambda k: k['at'], reverse=True)
    if not request.json or not 'loc' in request.json:
        abort(400)
    return jsonify( { 'spots': map(make_public_spot, sorted_spots) } )

if __name__ == '__main__':
#    app.run(debug = True)
    import logging, logging.config, yaml
    logging.config.dictConfig(yaml.load(open('logging.conf')))
    logfile    = logging.getLogger('file')
    logconsole = logging.getLogger('console')
    logfile.debug("Debug FILE")
    logconsole.debug("Debug CONSOLE")

    app.run(host="0.0.0.0")
