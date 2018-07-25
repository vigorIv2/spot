#!flask/bin/python

import time

# import json
import psycopg2

import logging, logging.config, yaml
logging.config.dictConfig(yaml.load(open('logging.conf')))
logfl    = logging.getLogger('file')
logconsole = logging.getLogger('console')
logfl.debug("Debug FILE")
logconsole.debug("Debug CONSOLE")

def openConn():
	global conn
	global cur
#	conn = psycopg2.connect(database="huhula", user="root", host="roachdb", port=26257)
        cs = "postgresql://huhuladb00:26257/huhula?user=huhulaman&sslcert=/home/ubuntu/spot/certs/client.huhulaman.crt&sslkey=/home/ubuntu/spot/certs/client.huhulaman.key&sslmode=require&ssl=true"
        conn = psycopg2.connect(cs)

	conn.set_session(autocommit=True)
	cur = conn.cursor()

def getUserProperties(uid) :
	cur.execute("SELECT roles FROM users WHERE id = '%s'" % (uid,))
	row=cur.fetchone()
	if row:
		return row
	else:
		return None

def cleanUp(users) :
        for u in users:
	    informer_id=getUserID(u)
            if informer_id != None:
                logconsole.info("Cleaning up for user "+str(u)+" uid="+str(informer_id))
	        cur.execute("delete FROM occupy WHERE taker_id = '%s'" % (informer_id,))
	        cur.execute("delete FROM parked WHERE informer_id = '%s'" % (informer_id,))
	        cur.execute("delete FROM spots WHERE informer_id = '%s'" % (informer_id,))
	        cur.execute("delete FROM users WHERE userhash = '%s'" % (u,))

def getUserID(user) :
	cur.execute("SELECT id FROM users WHERE userhash = '%s'" % (user,))
	row=cur.fetchone()
	if row:
		return row[0]
	else:
		return None

def checkSameSpot(informer_id,spot,lat,lon) :
	selsql = """select count(*) as cnt 
		from huhula.spots 
		where quantity > 0
			and informer_id = '%s' 
			and array_position(direction,%s) is not null
			and round(longitude,4) = round(%s,4) 
			and round(latitude,4) = round(%s,4) 
		""" % (informer_id, spot, lon, lat,)
        logconsole.debug("SQL:" + selsql)
 	cur.execute(selsql)
	row=cur.fetchone()
	if row:
		return row[0]
	else:
		return None

def locateSpot(latitude0,longitude0) :
        selsql = """select id, spot, age, sqrt(df*df + dl*dl) * 6371e3 as dist, latitude, longitude from (
		select sp.id, direction[1] as spot, age(sp.inserted_at) as age, 
			(longitude*pi()/180 - %s*pi()/180) * cos((latitude*pi()/180 + %s*pi()/180)/2) as dl,
			(latitude*pi()/180 - %s*pi()/180) as df, latitude, longitude from huhula.spots as sp   
		where quantity > 0 -- and age(sp.inserted_at) < INTERVAL '2d2h1m1s1ms1us6ns'
		order by age(sp.inserted_at) 
  		) where sqrt(df*df + dl*dl) * 6371e3 < 2000000 
		  order by sqrt(df*df + dl*dl) * 6371e3, age
  		limit 1""" % (longitude0,latitude0,latitude0,)
        logconsole.debug("SQL:" + selsql)
	cur.execute(selsql)
        row=cur.fetchone()
        if row:
                return row
        else:
                return None

def getReportedSpots(rid,hd) :
	if rid.isnumeric():
		informer_id=getUserID(rid)
	else:
		informer_id=rid
	if informer_id == None: 
		return 404
        selsql = "select longitude, latitude from huhula.spots as sp where sp.informer_id = '%s' and age(sp.inserted_at) < INTERVAL '%sh'" % (informer_id,hd,)
        logconsole.debug("SQL:" + selsql)
        cur.execute(selsql)
        rows=cur.fetchall()
        if rows:
                return rows
        else:
                return None

def getParkedSpots(rid,hd) :
	if rid.isnumeric():
		informer_id=getUserID(rid)
	else:
		informer_id=rid
	if informer_id == None: 
		return 404
        selsql = "select longitude, latitude from huhula.parked as sp where sp.informer_id = '%s' and age(sp.inserted_at) < INTERVAL '%sh'" % (informer_id,hd,)
        logconsole.debug("SQL:" + selsql)
        cur.execute(selsql)
        rows=cur.fetchall()
        if rows:
                return rows
        else:
                return None

def getNearSpots(lt,lg,hd) :
        selsql = """select longitude, latitude from (
                select sp.id, age(sp.inserted_at) as age, 
                        (longitude*pi()/180 - %s*pi()/180) * cos((latitude*pi()/180 + %s*pi()/180)/2) as dl,
                        (latitude*pi()/180 - %s*pi()/180) as df, latitude, longitude from huhula.spots as sp   
                where quantity > 0 and age(sp.inserted_at) < INTERVAL '%sh'
                order by age(sp.inserted_at) 
                ) where sqrt(df*df + dl*dl) * 6371e3 < 2000 
                  order by sqrt(df*df + dl*dl) * 6371e3, age
                limit 1000""" % (lg,lt,lt,hd,)
        logconsole.debug("SQL:" + selsql)
        cur.execute(selsql)
        rows=cur.fetchall()
        if rows:
                return rows
        else:
                return None


def newUser(user) :
	cur.execute("INSERT INTO huhula.users(userhash) values(%s)",(user,))


def insertParked(informer,informed_at,azimuth,altitude,longitude,latitude,client_at) :
	informer_id=getUserID(informer)
	if ( informer_id is None ) :
		return 404
	cur.execute("INSERT INTO huhula.parked(informer_id,informed_at,azimuth,altitude,longitude,latitude,client_at) values(%s,%s,%s,%s,%s,%s,%s)",
            (informer_id,informed_at,azimuth,altitude,longitude,latitude,client_at))
	return 0

def insertSpot(informer,informed_at,azimuth,altitude,longitude,latitude,spots,client_at,mode,qty) :
	informer_id=getUserID(informer)
	if ( informer_id is None ) :
		return 404
#		newUser(informer)
#		informer_id=getUserID(informer)
	sameSpot = checkSameSpot(informer_id,spots[0],latitude,longitude)
	if (sameSpot is None) or (sameSpot == 0) : 
		cur.execute("INSERT INTO huhula.spots(informer_id,informed_at,azimuth,altitude,longitude,latitude,direction,quantity,client_at,mode) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (informer_id,informed_at,azimuth,altitude,longitude,latitude,spots,qty,client_at,mode))
	        return 0		
	else :
		return 409

def occupySpot(taker,sid,taken_at,client_at) :
	taker_id=getUserID(taker)
	if ( taker_id is None ) :
		return 404
		
	cur.execute("update huhula.spots set quantity=quantity-1 where id=%s and quantity > 0", (sid,))
	if cur.rowcount > 0:
	  cur.execute("INSERT INTO huhula.occupy(spot_id, taken_at, taker_id, client_at) values(%s,now(),%s,%s)", (sid, taker_id, client_at))	
	else:
	  return 404	  
	return 0	
