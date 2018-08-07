#!flask/bin/python

import time
import traceback
import datetime

# import json
import psycopg2
from psycopg2.pool import SimpleConnectionPool

import logging, logging.config, yaml
logging.config.dictConfig(yaml.load(open('logging.conf')))
logfl    = logging.getLogger('file')
logconsole = logging.getLogger('console')
logfl.debug("Debug FILE")
logconsole.debug("Debug CONSOLE")

def initPool():
    global g_pool
    cs = "postgresql://huhuladb00:26257/huhula?user=huhulaman&sslcert=/home/ubuntu/spot/certs/client.huhulaman.crt&sslkey=/home/ubuntu/spot/certs/client.huhulaman.key&sslmode=require&ssl=true"
    g_pool = SimpleConnectionPool(1, 9, cs)

#    con = g_pool.getconn()
#    con.set_session(autocommit=True)
#    g_pool.putconn(con)

initPool()

def openConnoldStyle():
	global conn
	global cur
#	conn = psycopg2.connect(database="huhula", user="root", host="roachdb", port=26257)
        cs = "postgresql://huhuladb00:26257/huhula?user=huhulaman&sslcert=/home/ubuntu/spot/certs/client.huhulaman.crt&sslkey=/home/ubuntu/spot/certs/client.huhulaman.key&sslmode=require&ssl=true"
        conn = psycopg2.connect(cs)

	conn.set_session(autocommit=True)
	cur = conn.cursor()

def getInformedSpots(uid,dfrom,dto) :
       	lconn = g_pool.getconn()
	cur = lconn.cursor() 
        try:
	    cur.execute("""select sum(orig_quantity) as qty, informer_id as uid, min(inserted_at) as mnat, max(inserted_at) as mxat, count(*) as cnt
                            from spots 
                            where informer_id = '%s' and inserted_at between '%s' and '%s'
                            group by informer_id;""" % (uid,dfrom,dto))
	    row=cur.fetchone()
	    if row:
		return row
	    else:
		return None
        finally:
	    cur.close()		
            lconn.commit()
            g_pool.putconn(lconn)

def getOccupiedSpots(uid,dfrom,dto) :
       	lconn = g_pool.getconn()
	cur = lconn.cursor() 
        try:
	    cur.execute("""select count(*) as qty, taker_id as uid, min(inserted_at) as mnat, max(inserted_at) as mxat 
                            from occupy
                            where taker_id = '%s' and inserted_at between '%s' and '%s'
                            group by taker_id;""" % (uid,dfrom,dto))
	    row=cur.fetchone()
	    if row:
		return row
	    else:
		return None
        finally:
	    cur.close()		
            lconn.commit()
            g_pool.putconn(lconn)

def getUserProperties(uid) :
       	lconn = g_pool.getconn()
	cur = lconn.cursor() 
        try:
	    cur.execute("SELECT roles FROM users WHERE id = '%s'" % (uid,))
	    row=cur.fetchone()
	    if row:
		return row
	    else:
		return None
        finally:
	    cur.close()		
            lconn.commit()
            g_pool.putconn(lconn)

def getUserBalance(user) :
       	lconn = g_pool.getconn()
	cur = lconn.cursor() 
        try:
	    cur.execute("SELECT id,balance FROM users WHERE userhash = '%s'" % (user,))
	    row=cur.fetchone()
            if row == None:
                return None
            informer_id = row[0]
            balance = str(row[1])
	    cur.execute("select sum(informed_qty) as iqty, sum(occupied_qty) as octy, sum(gift) as gift, sum(penalty) as penalty, sum(balance) as balance from huhula.bill_payable where user_id = '%s'" % (informer_id,))
	    row2=cur.fetchone()
            if row2:
		return (balance,str(row2[0]),str(row2[1]),str(row2[2]),str(row2[3]),str(row2[4]))
	    else:
		return None
        finally:
	    cur.close()		
            lconn.commit()
            g_pool.putconn(lconn)

def cleanUp(users) :
        for u in users:
	    informer_id=getUserID(u)
            if informer_id != None:
                logconsole.info("Cleaning up derivatives for user "+str(u)+" uid="+str(informer_id))
        	lconn = g_pool.getconn()
                lconn.set_session(autocommit=True)

		cur = lconn.cursor() 
		try:
	        	cur.execute("delete FROM occupy WHERE taker_id = '%s'" % (informer_id,))
	        	cur.execute("delete FROM parked WHERE informer_id = '%s'" % (informer_id,))
	        	cur.execute("delete FROM bill WHERE user_id = '%s'" % (informer_id,))
		finally:
			cur.close()		
        		g_pool.putconn(lconn)
        for u in users:
	    informer_id=getUserID(u)
            if informer_id != None:
                logconsole.info("Cleaning up root recs for user "+str(u)+" uid="+str(informer_id))
        	lconn = g_pool.getconn()
                lconn.set_session(autocommit=True)

		cur = lconn.cursor() 
		try:
	        	cur.execute("delete FROM spots WHERE informer_id = '%s'" % (informer_id,))
	        	cur.execute("delete FROM users WHERE userhash = '%s'" % (u,))
		finally:
			cur.close()		
        		g_pool.putconn(lconn)

def getUserID(user) :
        lconn = g_pool.getconn()
	cur = lconn.cursor() 
	cur.execute("SELECT id FROM users WHERE userhash = '%s'" % (user,))
	row = cur.fetchone()
	try: 
		if row:
			return row[0]
		else:
			return None
	finally:
		cur.close()
                lconn.commit()
        	g_pool.putconn(lconn)


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
       	lconn = g_pool.getconn()
	cur = lconn.cursor() 
        try:
            cur.execute(selsql)
            row=cur.fetchone()
            if row:
                    return row[0]
            else:
                    return None
        finally:
	    cur.close()
            lconn.commit()
            g_pool.putconn(lconn)


def locateSpot(latitude0,longitude0) :
        selsql = """select id, spot, substring(cast(age as string),1,16) as age, sqrt(df*df + dl*dl) * 6371e3 as dist, latitude, longitude from (
		select sp.id, direction[1] as spot, sp.inserted_at as age,
			(longitude*pi()/180 - %s*pi()/180) * cos((latitude*pi()/180 + %s*pi()/180)/2) as dl,
			(latitude*pi()/180 - %s*pi()/180) as df, latitude, longitude from huhula.spots as sp   
		where quantity > 0 -- and age(sp.inserted_at) < INTERVAL '2d2h1m1s1ms1us6ns'
		order by age(sp.inserted_at)
  		) where sqrt(df*df + dl*dl) * 6371e3 < 2000
		  order by sqrt(df*df + dl*dl) * 6371e3, age desc
  		limit 30""" % (longitude0,latitude0,latitude0,)
        logconsole.debug("SQL:" + selsql)
       	lconn = g_pool.getconn()
	cur = lconn.cursor() 
        try:
	    cur.execute(selsql)
            row=cur.fetchall()
            if row:
                return row
            else:
                return None
        finally:
	    cur.close()
            lconn.commit()
            g_pool.putconn(lconn)


def getReportedSpots(rid,hd) :
	if rid.isnumeric():
		informer_id=getUserID(rid)
	else:
		informer_id=rid
	if informer_id == None: 
		return 404
        selsql = "select longitude, latitude from huhula.spots as sp where sp.informer_id = '%s' and age(sp.inserted_at) < INTERVAL '%sh'" % (informer_id,hd,)
        logconsole.debug("SQL:" + selsql)
       	lconn = g_pool.getconn()
	cur = lconn.cursor() 
        try:
            cur.execute(selsql)
            rows=cur.fetchall()
            if rows:
                return rows
            else:
                return None
        finally:
	    cur.close()
            lconn.commit()
            g_pool.putconn(lconn)

def getParkedSpots(rid,hd) :
	if rid.isnumeric():
		informer_id=getUserID(rid)
	else:
		informer_id=rid
	if informer_id == None: 
		return 404
        selsql = "select longitude, latitude from huhula.parked as sp where sp.informer_id = '%s' and age(sp.inserted_at) < INTERVAL '%sh'" % (informer_id,hd,)
        logconsole.debug("SQL:" + selsql)
       	lconn = g_pool.getconn()
	cur = lconn.cursor() 
        try:
            cur.execute(selsql)
            rows=cur.fetchall()
            if rows:
                return rows
            else:
                return None
        finally:
	    cur.close()
            lconn.commit()
            g_pool.putconn(lconn)

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
       	lconn = g_pool.getconn()
	cur = lconn.cursor() 
        try:
            cur.execute(selsql)
            rows=cur.fetchall()
            if rows:
                return rows
            else:
                return None
        finally:
	    cur.close()
            lconn.commit()
            g_pool.putconn(lconn)


def newUser(user) :
       	lconn = g_pool.getconn()
	cur = lconn.cursor() 
        try:
	    cur.execute("INSERT INTO huhula.users(userhash) values(%s)",(user,))
            lconn.commit()
        except Exception as error:
            jts = traceback.format_exc()
            logconsole.error(jts)
            lconn.rollback()
        finally:
	    cur.close()
            g_pool.putconn(lconn)


def insertParked(informer,informed_at,azimuth,altitude,longitude,latitude,client_at) :
	informer_id=getUserID(informer)
	if ( informer_id is None ) :
		return 404
       	lconn = g_pool.getconn()
	cur = lconn.cursor() 
        try:
	    cur.execute("INSERT INTO huhula.parked(informer_id,informed_at,azimuth,altitude,longitude,latitude,client_at) values(%s,%s,%s,%s,%s,%s,%s)",
                (informer_id,informed_at,azimuth,altitude,longitude,latitude,client_at))
            lconn.commit()
        except Exception as error:
            jts = traceback.format_exc()
            logconsole.error(jts)
            lconn.rollback()
        finally:
	    cur.close()
            g_pool.putconn(lconn)
	return 0


def last_day_of_month(any_day):
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
        result = next_month - datetime.timedelta(days=next_month.day)
        return str(result)

def upsertBill(pconn, user_id, for_date, informed_qty_delta, occupied_qty_delta) :
	cur = pconn.cursor() 
        try:
            # first attempt to update, if it yeilds zero affected rows that meants it needs to be inserted
	    usql = "update huhula.bill set updated_at=now(), informed_qty=informed_qty+%s, occupied_qty=occupied_qty+%s where user_id='%s' and for_date=cast('%s' as date)" % (informed_qty_delta, occupied_qty_delta, user_id, for_date)
            logconsole.debug("update bill sql:" + usql)
	    cur.execute(usql)
            if cur.rowcount == 0:
                isql = "INSERT INTO huhula.bill(user_id, for_date, informed_qty, occupied_qty) values('%s',cast('%s' as date),%s,%s)" % (user_id, for_date, informed_qty_delta, occupied_qty_delta)
                logconsole.debug("insert bill sql:" + isql)
	        cur.execute(isql)
        except Exception as error:
            jts = traceback.format_exc()
            logconsole.error(jts)
	    raise Exception('Exception while update bill', 'Bill Update Error')
        finally:
	    cur.close()

def insertSpot(informer,informed_at,azimuth,altitude,longitude,latitude,spots,client_at,mode,qty) :
	informer_id=getUserID(informer)
	if ( informer_id is None ) :
		return 404
#		newUser(informer)
#		informer_id=getUserID(informer)
	sameSpot = checkSameSpot(informer_id,spots[0],latitude,longitude)
       	lconn = g_pool.getconn()
	cur = lconn.cursor() 
        try:
	    if (sameSpot is None) or (sameSpot == 0) : 
		cur.execute("INSERT INTO huhula.spots(informer_id,informed_at,azimuth,altitude,longitude,latitude,direction,quantity,orig_quantity,client_at,mode) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (informer_id,informed_at,azimuth,altitude,longitude,latitude,spots,qty,qty,client_at,mode))
                upsertBill(lconn,informer_id, last_day_of_month(datetime.datetime.fromtimestamp(informed_at/1000.0)), qty, 0)
                lconn.commit()
	        return 0		
	    else :
		return 409
        except Exception as error:
            jts = traceback.format_exc()
            logconsole.error(jts)
            lconn.rollback()
        finally:
	    cur.close()
            g_pool.putconn(lconn)

def getInformerID(sid) :
        lconn = g_pool.getconn()
        cur = lconn.cursor() 
        cur.execute("SELECT informer_id FROM spots WHERE id = '%s' and quantity > 0" % (sid,))
        row = cur.fetchone()
        try: 
                if row:
                        return row[0]
                else:
                        return None
        finally:
                cur.close()
                lconn.commit()
                g_pool.putconn(lconn)


def occupySpot(taker,sid,taken_at,client_at) :
	taker_id=getUserID(taker)
	if ( taker_id is None ) :
		return 404
		
       	lconn = g_pool.getconn()
	cur = lconn.cursor() 
        try:
	    informer_id = getInformerID(sid)
	    if informer_id != None:
	    	cur.execute("update huhula.spots set quantity=quantity-1 where id=%s and quantity > 0", (sid,))
	    	if cur.rowcount > 0:
	        	cur.execute("INSERT INTO huhula.occupy(spot_id, taken_at, taker_id, client_at) values(%s,now(),%s,%s)", (sid, taker_id, client_at))	
                	upsertBill(lconn,informer_id, last_day_of_month(datetime.datetime.fromtimestamp(taken_at/1000.0)), 1, 0) # transfer one token from taker to informer
                	upsertBill(lconn,taker_id, last_day_of_month(datetime.datetime.fromtimestamp(taken_at/1000.0)), 0, 1)
                	lconn.commit()
	    	else:
	        	return 404
	    else:
		return 404	  
        except Exception as error:
            jts = traceback.format_exc()
            logconsole.error(jts)
            lconn.rollback()
        finally:
	    cur.close()
            g_pool.putconn(lconn)
	return 0	
