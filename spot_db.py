#!flask/bin/python

import time

# import json
import psycopg2

import logging, logging.config, yaml
logging.config.dictConfig(yaml.load(open('logging.conf')))
logfile    = logging.getLogger('file')
logconsole = logging.getLogger('console')
logfile.debug("Debug FILE")
logconsole.debug("Debug CONSOLE")

def openConn():
	global conn
	global cur
	conn = psycopg2.connect(database="huhula", user="root", host="roachdb", port=26257)
	conn.set_session(autocommit=True)
	cur = conn.cursor()

def getUserID(user) :
	cur.execute("SELECT id FROM users WHERE userhash = '" + user + "'")
	row=cur.fetchone()
	if row:
		return row[0]
	else:
		return None

def checkSameSpot(informer_id,spot,lat,lon) :
	selsql = """select count(*) as cnt 
		from huhula.spots 
		where taker_id is null 
			and informer_id = '%s' 
			and spot = %s
			and round(longitude,4) = round(%s,4) 
			and round(latitude,4) = round(%s,4) 
		""" % (informer_id, spot, lon, lat,)
        logfile.debug("SQL:" + selsql)
 	cur.execute(selsql)
	row=cur.fetchone()
	if row:
		return row[0]
	else:
		return None

def locateSpot(latitude0,longitude0) :
        selsql = """select id, spot, age, sqrt(df*df + dl*dl) * 6371e3 as dist, latitude, longitude from (
		select sp.id, sp.spot, age(sp.inserted_at) as age, 
			(longitude*pi()/180 - %s*pi()/180) * cos((latitude*pi()/180 + %s*pi()/180)/2) as dl,
			(latitude*pi()/180 - %s*pi()/180) as df, latitude, longitude from huhula.spots as sp   
		where taker_id is null -- and age(sp.inserted_at) < INTERVAL '2d2h1m1s1ms1us6ns'
		order by age(sp.inserted_at) 
  		) where sqrt(df*df + dl*dl) * 6371e3 < 2000000 
		  order by sqrt(df*df + dl*dl) * 6371e3, age
  		limit 1""" % (longitude0,latitude0,latitude0,)
        logfile.debug("SQL:" + selsql)
	cur.execute(selsql)
        row=cur.fetchone()
        if row:
                return row
        else:
                return None


def newUser(user) :
	cur.execute("INSERT INTO huhula.users(userhash) values(%s)",(user,))


def insertSpot(informer,informed_at,azimuth,altitude,longitude,latitude,spot,client_at) :
	informer_id=getUserID(informer)
	if ( informer_id is None ) :
		return 404
#		newUser(informer)
#		informer_id=getUserID(informer)
	sameSpot = checkSameSpot(informer_id,spot,latitude,longitude)
	if (sameSpot is None) or (sameSpot == 0) : 
		cur.execute("INSERT INTO huhula.spots(informer_id,informed_at,azimuth,altitude,longitude,latitude,spot,client_at) values(%s,%s,%s,%s,%s,%s,%s,%s)",
            (informer_id,informed_at,azimuth,altitude,longitude,latitude,spot,client_at))
	        return 0		
	else :
		return 409

def updateSpot(taker,sid,taken_at,client_at) :
	taker_id=getUserID(taker)
	if ( taker_id is None ) :
		return 404
		
	cur.execute("update huhula.spots set taken_at=now(), taker_id=%s where id=%s",
            (taker_id,sid))
	return 0	