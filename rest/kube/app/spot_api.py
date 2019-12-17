#!flask/bin/python

from flask import Flask, jsonify, abort, request, make_response, url_for, Response
import time
from flask_httpauth import HTTPBasicAuth
import datetime

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

def make_public_user(user):
    new_user = {}
    for field in user:
      if field != 'wallet': # skip wallet - it is misleading 
         new_user[field] = user[field]
    return new_user

def make_public_spot(spot):
    new_spot = {}
    for field in spot:
            new_spot[field] = spot[field]
    return new_spot

def make_public_balance(bal):
    new_bal = {}
    for field in bal:
        new_bal[field] = bal[field]
    return new_bal

def make_public_reference(ref):
    new_ref = {}
    for field in ref:
        new_ref[field] = ref[field]
    return new_ref

def make_public_referral(ref):
    new_ref = {}
    for field in ref:
        new_ref[field] = ref[field]
    return new_ref

def data_points(arr):
    mn = min(arr)
    mx = max(arr)
    av = (mx - mn) / len(arr)
    return mn,mx,av+mn

@app.route('/spot/api/v1.0/usage', methods = ['GET'])
#@auth.login_required
def get_usage():
    hd = request.args.get('hd', "8760")
    if not hd.isdigit():
      hd = "8760"
    logconsole.info("running usage with hd="+str(hd))
    usage_array=spot_db.getSpotClusters(hd)
    logconsole.info("coords usage returned "+str(usage_array))
    html = "<html><body><h1>Empty</h1></body></html>"
    if usage_array != None and len(usage_array) > 0:
        html = "<html><body><table border='1' cellpadding='0' cellspacing='0' width='400px'>"
        html += "<tr><th>Qty</th><th>Date</th><th>Lon</th><th>Lat</th><th>map</th></tr>"
        for r in usage_array:
           html += "<tr><td>"+str(r[0])+"</td><td>"+str(r[1])+"</td><td>"+str(r[2])+"</td><td>"+str(r[3])+"<td><a href=\"/spot/api/v1.0/map?hd=8760&lt="+str(r[3])+"&lg="+str(r[2])+"\">map</a></td></tr>"
        html += "</table></body></html>"
    resp = make_response(html, 200)
    resp.headers['Content-type'] = 'text/html'
    return resp

@app.route('/spot/api/v1.0/map', methods = ['GET'])
#@auth.login_required
def get_map():
    mid = request.args.get('mid', None)
    pid = request.args.get('pid', None)
    hd = request.args.get('hd', "24")
    if not hd.isdigit():
      hd = "24"
    lt = request.args.get('lt', None)
    lg = request.args.get('lg', None)
    logconsole.info("running map with "+str(request.args)+" lt="+str(lt)+" lg="+str(lg)+" mid="+str(mid)+" pid="+str(pid)+" hd="+str(hd))
    if lt == None and lg == None and mid == None and pid == None :
        abort(400)
    coord_array = []
    if pid != None: 
       coord_array=spot_db.getParkedSpots(pid,hd)
       if coord_array != None and len(coord_array) > 0:
          mn0,mx0,lg=data_points(list(map(lambda x: x[0], coord_array)))
          mn1,mx1,lt=data_points(list(map(lambda x: x[1], coord_array)))
          logconsole.debug("determined parked mn0="+str(mn0)+" mx0="+str(mx0))
          logconsole.debug("determined parked mn1="+str(mn1)+" mx1="+str(mx1))
       logconsole.debug("determined parked lt="+str(lt)+" lg="+str(lg)+" for mid="+str(pid))
    else:
       if mid != None: 
          coord_array=spot_db.getReportedSpots(mid,hd)
          if coord_array != None and len(coord_array) > 0:
             mn0,mx0,lg=data_points(list(map(lambda x: x[0], coord_array)))
             mn1,mx1,lt=data_points(list(map(lambda x: x[1], coord_array)))
             logconsole.debug("determined reported mn0="+str(mn0)+" mx0="+str(mx0))
             logconsole.debug("determined reported mn1="+str(mn1)+" mx1="+str(mx1))
          logconsole.debug("determined reported lt="+str(lt)+" lg="+str(lg)+" for mid="+str(mid))
       else:
          coord_array=spot_db.getNearSpots(lt,lg,hd)
    logconsole.info("coords returned "+str(coord_array))
    ufilename = "maps/ag_"+uuid.uuid4().hex+".kml"
    if coord_array != None and len(coord_array) > 0: 
       spot_kml.gen_kml(coord_array, ufilename)
       html=spot_kml.gen_html(lt, lg, ufilename)
    else:
       html=spot_kml.gen_empty_html()
    resp = make_response(html, 200)
    resp.headers['Content-type'] = 'text/html'
    return resp

@app.route('/spot/api/v1.0/register', methods = ['POST'])
@auth.login_required
def get_newregister():
    logconsole.info("new register called with "+str(request.json))
    if not request.json or not 'id' in request.json:
        abort(400)
    user = {
        'id': request.json['id'],
        'wallet': '0x123415235',
        'created_at': time.time()
    }
    user_id=spot_db.getUserID(request.json['id'])
    refer = None
    if 'ref' in request.json:
       refer = request.json['ref']
    if user_id is None :
       spot_db.newUser(request.json['id'])
       user_id = spot_db.getUserID(request.json['id'])
       spot_db.giftBill(user_id, spot_db.last_day_of_month(datetime.datetime.fromtimestamp(time.time())), 20)
    props = spot_db.getUserProperties(user_id)
    logconsole.info("new registering user "+request.json['id']+" user_id="+user_id+" props="+str(props))
    if refer != None:
       (closedRefCnt,sender_id) = spot_db.closeReferral(refer,request.json['id'])
       if closedRefCnt is None or sender_id is None or closedRefCnt == 0 :
          logconsole.info("prevented attempt to use non existing or closed referral user_id="+user_id+" ref="+refer)
       else:
          spot_db.giftBill(user_id, spot_db.last_day_of_month(datetime.datetime.fromtimestamp(time.time())), 10)
          spot_db.giftBill(sender_id, spot_db.last_day_of_month(datetime.datetime.fromtimestamp(time.time())), 10)
          logconsole.info("reference accepted, tokens granted, user_id="+user_id+" sender_id="+sender_id+" ref="+refer)

    user['roles']=props[0]
    logconsole.info("new registered user "+request.json['id']+" db key ="+user_id+" props="+str(props))
    return jsonify( { 'user': make_public_user(user) } ), 201

@app.route('/spot/api/v1.0/oldregister', methods = ['POST'])
@auth.login_required
def get_register():
    logconsole.info("register called with "+str(request.json))
    if not request.json or not 'id' in request.json:
        abort(400)
    user = {
        'id': request.json['id'],
        'wallet': '0x12341q42134khjsagdf2345235',
        'created_at': time.time()
    }
    informer_id=spot_db.getUserID(request.json['id'])
    refer = None
    if 'ref' in request.json:
       refer = request.json['ref']
    if informer_id is None :
       spot_db.newUser(request.json['id'])
       informer_id=spot_db.getUserID(request.json['id'])
       spot_db.giftBill(informer_id, spot_db.last_day_of_month(datetime.datetime.fromtimestamp(time.time())), 20)
    props = spot_db.getUserProperties(informer_id)
    logconsole.info("registering user "+request.json['id']+" informer_id="+informer_id+" props="+str(props))
    if refer != None:
       sender_id = spot_db.getSenderId(refer)
       if sender_id == None:
          logconsole.info("attempt to re-use closed reference prevented informer_id="+informer_id+" ref="+refer)
       else:
          if sender_id == informer_id:
             logconsole.info("attempt to self refer prevented informer_id="+informer_id+" ref="+refer)
          else:
             rc = spot_db.closeReferrence(refer, informer_id)
             if rc != 0:
                abort(rc)
             spot_db.giftBill(informer_id, spot_db.last_day_of_month(datetime.datetime.fromtimestamp(time.time())), 10)
             spot_db.giftBill(sender_id, spot_db.last_day_of_month(datetime.datetime.fromtimestamp(time.time())), 10)
             logconsole.info("reference accepted, tokens granted, informer_id="+informer_id+" sender_id="+sender_id+" ref="+refer)

    user['roles']=props[0]
    logconsole.info("registered user "+request.json['id']+" db key ="+informer_id+" props="+str(props))
    return jsonify( { 'user': make_public_user(user) } ), 201

@app.route('/spot/api/v1.0/refer', methods = ['POST'])
@auth.login_required
def get_refer():
    logconsole.info("refer called with "+str(request.json))
    if not request.json or not 'id' in request.json:
        abort(400)
    reference = {
        'id': request.json['id'],
    }
    ref_id=spot_db.newReference(request.json['id'])
    if ref_id is None :
        abort(400)
    reference['ref']=ref_id
    logconsole.info("reference response "+str(reference))
    return jsonify( { 'reference': make_public_reference(reference) } ), 201

@app.route('/spot/api/v1.0/referral', methods = ['POST'])
@auth.login_required
def get_referral():
    logconsole.info("referral called with "+str(request.json))
    if not request.json or not 'id' in request.json or not 'links' in request.json :
        logconsole.info("returning 400 id "+request.json['id']+" request "+str(request))
        abort(400)

    reference = {
        'id': request.json['id'],
        'rejected': []
    }
    referralsCnt=spot_db.countReferrals(request.json['id'])
    logconsole.info("number of user "+request.json['id']+" referrals is equal "+str(referralsCnt))
    non_members = [] 
    for link_hash in request.json['links']:
        if (len(non_members) + referralsCnt) >= 30:
             logconsole.info("user "+request.json['id']+" has referred plenty, preventing mass referrals" )
             reference['rejected'].append(link_hash)
        else:
             if link_hash == request.json['id']: 
                  logconsole.info("self reference attempt with link_hash "+link_hash+" prevented")
                  reference['rejected'].append(link_hash)
             else:
                  user_id = spot_db.getUserID(link_hash)
                  if user_id is None:
                      logconsole.info("user does not exist with link_hash "+link_hash+" checking if referal was sent")
                      ref_id = spot_db.getReferral(link_hash)
                      if ref_id is None:
                          logconsole.info("referal has not been sent for "+link_hash)
                          non_members.append(link_hash)
                      else:
                          logconsole.info("referal has already been sent for link_hash "+link_hash)
                          reference['rejected'].append(link_hash)
                  else:
                      logconsole.info("user exists with link_hash "+link_hash)
                      reference['rejected'].append(link_hash)
    if len(non_members) > 0: # some candidate not registered yet
        logconsole.info("adding non_members "+str(non_members))
        if not 'dryrun' in request.json: 
           ref_id=spot_db.newReferral(request.json['id'],non_members)
           if ref_id is None:
              logconsole.info("returning 403 id "+request.json['id'])
              abort(403)
           reference['ref']=ref_id
    else:
        logconsole.info("all referral candidates were rejected")
      
    logconsole.info("referral response "+str(reference))
    return jsonify( { 'referral': make_public_referral(reference) } ), 201

@app.route('/spot/api/v1.0/balance', methods = ['POST'])
@auth.login_required
def get_balance():
    logconsole.info("balance called with "+str(request.json))
    if not request.json or not 'id' in request.json:
        abort(400)
    bal = {
        'id': request.json['id'],
    }
    balance = spot_db.getUserBalance(request.json['id'])
    if balance is None :
        abort(400)
    logconsole.info("balance balance=" + str(balance))
    bal['wallet_balance'] = balance[0]
    bal['iqty'] = balance[1]
    bal['oqty'] = balance[2]
    bal['gift'] = balance[3]
    bal['penalty'] = balance[4]
    bal['new_balance'] = balance[5]

    logconsole.info("balance bal=" + str(bal))
    return jsonify( { 'balance': make_public_balance(bal) } ), 201

@app.route('/spot/api/v1.0/spot', methods = ['POST'])
@auth.login_required
def get_spot():
    logconsole.info("get_spot called with "+str(request.json))
    if not request.json or not 'uid' in request.json:
        abort(400)
    if not request.json or not 'loc' in request.json:
        abort(400)
    if not request.json or not 'spot' in request.json:
        abort(400)
    if not request.json or not 'deg' in request.json:
        abort(400)
    mode=1 if request.json.get('m', 0) == 'a' else 0 # by default treat as manually reported - aka 0
    qty=request.json.get('q', len(request.json['spot'])) # by default fill up quantity as number of elements in location array
    spot = {
        'id': "h2",
        'uid': request.json['uid'], 
        'loc': request.json['loc'],
        'spot' : request.json['spot'],
        'deg' : request.json['deg'],
        'at': time.time(),
        'ct': request.json['ct'],
        'm': mode,
        'q': qty,
    }
    rc = spot_db.insertSpot(request.json['uid'],int(round(time.time() * 1000)),request.json['deg'],request.json['loc']['al'],
            request.json['loc']['lg'],request.json['loc']['lt'],request.json['spot'],request.json['ct'],mode,qty)
    if ( rc != 0 ):
        abort(rc) 

    return jsonify( { 'spot': make_public_spot(spot) } ), 201

@app.route('/spot/api/v1.0/take', methods = ['POST'])
@auth.login_required
def get_take():
    logconsole.info("get_take called with "+str(request.json))
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
    # 2018-05-08 02:57:27,299 - file - DEBUG - Take called with {u'loc': {u'lg': 6.7, u'lt': 3.4, u'al': 5.9}, u'ct': u'12121212121212', u'uid': u'igor', u'sid': u'jhgjhgjhgjhgjhgjhgjhg'}
    rc = spot_db.occupySpot(request.json['uid'],request.json['sid'],int(round(time.time() * 1000)),request.json['ct'])
    if ( rc != 0 ):
        abort(rc)
    return jsonify( { 'spot': make_public_spot(spot) } ), 201

@app.route('/spot/api/v1.0/park', methods = ['POST'])
@auth.login_required
def get_park():
    logconsole.info("get_park called with "+str(request.json))
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
    rc = spot_db.insertParked(request.json['uid'],int(round(time.time() * 1000)),request.json['deg'],request.json['loc']['al'],
       request.json['loc']['lg'],request.json['loc']['lt'],request.json['ct'])
    if ( rc != 0 ):
       abort(rc)

    return jsonify( { 'spot': make_public_spot(spot) } ), 201

@app.route('/spot/api/v1.0/locate', methods = ['POST'])
@auth.login_required
def get_locate():
    logconsole.info("locate called with "+str(request.json))

    if not request.json or not 'loc' in request.json:
        abort(400)

    results=spot_db.locateSpot(request.json['loc']['lt'],request.json['loc']['lg'])
    logconsole.debug("Locate found in db "+str(results))
    if results == None:
        abort(404)

# Locate called with {u'loc': {u'lg': -117.71802732, u'lt': 33.58032164, u'al': 73}}
# Locate found in db ('c1a1defc-0d93-427c-b0d7-601e08d1637d', 0L, datetime.timedelta(660), 4.63180451482997, 33.58035109, -117.71799196)
    gspots = []
    for res in results:
        logconsole.debug("Locate debugging res="+str(res))
        sid = res[0]
        lg = res[5]
        lt = res[4]
        spot = res[1]
        age = str(res[2])
        dist = str(round(res[3],1))
        logconsole.debug("Locate debugging spot="+str(spot)+" sid="+str(sid)+" age="+age+" age="+age+" dist="+dist)
        gspots += [{
                "sid": sid,
                "dist": dist,
                "age": age,
                "loc": {
                    "al": 0,
                    "lg": lg,
                    "lt": lt
                },
                "spot": [ spot ],
            }]
    logconsole.info("Locate constructed json response "+str(gspots))

    return jsonify( { 'spots': map(make_public_spot, gspots) } )

if __name__ == '__main__':
#    app.run(debug = True)

    app.run(host="0.0.0.0")
