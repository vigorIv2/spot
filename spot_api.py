#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for
import time
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__, static_url_path = "")
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'testuser':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog
    
@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

users = [
    {
        'id': "blah",
        'wallet': '0x12341q42134khjsagdf2345235',
        'created_at': '2017-01-02 00:02:03', 
    },
    {
        'id': "blah2",
        'wallet': '0x12341412134khjsagdf2345235',
        'created_at': '2017-11-02 00:02:03', 
    }
]

spots = [
    {
        'id': "blah",
        'uid': "blh", 
        'loc': {
            "lt" : 125.12,
            "lg" : 23.234,
            "al" : 3434.12
            },
        'spot' : [1,2,3,4],
        'deg' : 12.12,
        'at': '2017-01-02 00:02:03', 
    },
    {
        'id': "blah2",
        'uid': "blh", 
        'loc': {
            "lt" : 145.12,
            "lg" : 34.234,
            "al" : 34.12
            },
        'spot' : [3,4],
        'deg' : 1.2,
        'at': '2017-01-02 00:02:03', 
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
    return jsonify( { 'spots': map(make_public_spot, spots) } )

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
    }
    spots.append(spot)
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
    }
    spots.append(spot)
    return jsonify( { 'spot': make_public_spot(spot) } ), 201

@app.route('/spot/api/v1.0/locate', methods = ['POST'])
@auth.login_required
def get_locate():
    if not request.json or not 'loc' in request.json:
        abort(400)
    return jsonify( { 'spots': map(make_public_spot, spots) } )

if __name__ == '__main__':
#    app.run(debug = True)
    import logging, logging.config, yaml
    logging.config.dictConfig(yaml.load(open('logging.conf')))
    logfile    = logging.getLogger('file')
    logconsole = logging.getLogger('console')
    logfile.debug("Debug FILE")
    logconsole.debug("Debug CONSOLE")

    app.run(host="0.0.0.0")
