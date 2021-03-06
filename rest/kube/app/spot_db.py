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
#       conn = psycopg2.connect(database="huhula", user="root", host="huhuladb00", port=26257)

# secure way :
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
                        cur.execute("delete FROM link WHERE referral_id = (select id from referral where sender_id = '%s')" % (informer_id,))
                        cur.execute("delete FROM referral where sender_id = '%s'" % (informer_id,))
                        cur.execute("delete FROM occupy WHERE taker_id = '%s'" % (informer_id,))
                        cur.execute("delete FROM parked WHERE informer_id = '%s'" % (informer_id,))
                        cur.execute("delete FROM bill WHERE user_id = '%s'" % (informer_id,))
                        cur.execute("delete FROM reference WHERE sender_id = '%s'" % (informer_id,))
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

def countReferrals(user) :
        sender_id=getUserID(user)
        if sender_id == None:
                return None
        lconn = g_pool.getconn()
        cur = lconn.cursor() 
        cur.execute("select count(*) from huhula.referral r inner join huhula.link l on (l.referral_id = r.id) where r.sender_id = '%s' and not l.updated_at is null " % (sender_id,))
        row = cur.fetchone()
        try: 
                if row:
                        return row[0]
                else:
                        return 0
        finally:
                cur.close()
                lconn.commit()
                g_pool.putconn(lconn)

def newReferral(user,non_members) :
        sender_id=getUserID(user)
        if sender_id == None:
            return None
        lconn = g_pool.getconn()
        cur = lconn.cursor()
        try: 
            cur.execute("INSERT INTO referral(sender_id) values(%s) RETURNING id;", (sender_id,))
            reference=cur.fetchone()[0]
            for to_hash in non_members:
                cur.execute("INSERT INTO link(referral_id,to_hash) values(%s,%s);", (reference,to_hash,))
            return reference
        except Exception as error:
            jts = traceback.format_exc()
            logconsole.error(jts)
            lconn.rollback()
            return None
        finally:
            cur.close()
            lconn.commit()
            g_pool.putconn(lconn)
        return None

def closeReferral(referral_id,user_hash) :
        lconn = g_pool.getconn()
        cur = lconn.cursor()
        try: 
            cur.execute("update link set updated_at=now() where referral_id=%s and to_hash=%s and updated_at is null ", (referral_id,user_hash,))
            rc = cur.rowcount
            sender_id = getReferralSender(referral_id)
            return (rc, sender_id)
        except Exception as error:
            jts = traceback.format_exc()
            logconsole.error(jts)
            lconn.rollback()
            return None
        finally:
            cur.close()
            lconn.commit()
            g_pool.putconn(lconn)
        return None

def getReferralSender(referral_id) :
        lconn = g_pool.getconn()
        cur = lconn.cursor() 
        cur.execute("select distinct sender_id from referral where id = '%s' " % (referral_id,))
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

def getReferral(userhash) :
        lconn = g_pool.getconn()
        cur = lconn.cursor() 
        cur.execute("SELECT referral_id FROM link WHERE to_hash = '%s'" % (userhash,))
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

def newReference(user) :
        sender_id=getUserID(user)
        if sender_id == None:
                return None
        lconn = g_pool.getconn()
        cur = lconn.cursor()
        try: 
                cur.execute("INSERT INTO reference(sender_id) values(%s) RETURNING id;", (sender_id,))
                reference=cur.fetchone()[0]     
                return reference
        finally:
                cur.close()
                lconn.commit()
                g_pool.putconn(lconn)
        return None

def closeReferrence(ref, receiver_id) :
        lconn = g_pool.getconn()
        cur = lconn.cursor()
        try:
           cur.execute("update reference set receiver_id=%s, updated_at=now() where receiver_id is null and id=%s", (receiver_id,ref,))
           if cur.rowcount == 0:
                return 404
        except Exception as error:
            jts = traceback.format_exc()
            logconsole.error(jts)
            lconn.rollback()
            return 404
        finally:
            cur.close()
            lconn.commit()
            g_pool.putconn(lconn)
        return 0

def getSenderId(ref) :
        lconn = g_pool.getconn()
        cur = lconn.cursor() 
        cur.execute("SELECT sender_id FROM reference WHERE receiver_id is null and id = '%s'" % (ref,))
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
                ) where sqrt(df*df + dl*dl) * 6371e3 < 300
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
        if '-' in rid:
                informer_id=rid
        else:
                informer_id=getUserID(rid)
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

def getAllNearSpots(lt,lg,hd) :
        selsql = """select longitude, latitude from (
                select sp.id, age(sp.inserted_at) as age, 
                        (longitude*pi()/180 - %s*pi()/180) * cos((latitude*pi()/180 + %s*pi()/180)/2) as dl,
                        (latitude*pi()/180 - %s*pi()/180) as df, latitude, longitude from huhula.spots as sp   
                where age(sp.inserted_at) < INTERVAL '%sh'
                order by age(sp.inserted_at) 
                ) where sqrt(df*df + dl*dl) * 6371e3 < 20000 
                  order by sqrt(df*df + dl*dl) * 6371e3, age
                """ % (lg,lt,lt,hd,)
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

def getSpotClusters(hd) :
        selsql = """select count(*), cast(max(s.inserted_at) as date), 
round(longitude,2) as lg, round(latitude,2) as lt
from huhula.spots s where age(s.inserted_at) < INTERVAL '%sh'
group by round(longitude,2), round(latitude,2)
order by round(longitude,2) limit 5000""" % (hd,)
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

def revokeRole(user,role) :
        lconn = g_pool.getconn()
        cur = lconn.cursor() 
        try:
            cur.execute("update huhula.users set roles=array_remove(roles,%s) where userhash=%s",(role,user,))
            lconn.commit()
        except Exception as error:
            jts = traceback.format_exc()
            logconsole.error(jts)
            lconn.rollback()
        finally:
            cur.close()
            g_pool.putconn(lconn)


def newUser(user) :
        lconn = g_pool.getconn()
        cur = lconn.cursor() 
        try:
            cur.execute("INSERT INTO huhula.users(userhash,roles) values(%s,array['promoter'])",(user,))
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

def giftBill(user_id, for_date, amount=0) :
        lconn = g_pool.getconn()
        cur = lconn.cursor() 
        try:
            # first attempt to update, if it yeilds zero affected rows that meants it needs to be inserted
            usql = "update huhula.bill set updated_at=now(), gift=gift+%s where user_id='%s' and for_date=cast('%s' as date)" % (amount, user_id, for_date)
            logconsole.debug("update bill gift sql:" + usql)
            cur.execute(usql)
            if cur.rowcount == 0:
                isql = "INSERT INTO huhula.bill(user_id, for_date, gift) values('%s',cast('%s' as date),%s)" % (user_id, for_date, amount)
                logconsole.debug("insert bill sql:" + isql)
                cur.execute(isql)
            lconn.commit()
        except Exception as error:
            jts = traceback.format_exc()
            logconsole.error(jts)
            lconn.rollback()
            raise Exception('Exception while update bill gift ', 'Bill Update Error')
        finally:
            cur.close()
            g_pool.putconn(lconn)

def insertSpot(informer,informed_at,azimuth,altitude,longitude,latitude,spots,client_at,mode,qty) :
        informer_id=getUserID(informer)
        if ( informer_id is None ) :
                return 404
#               newUser(informer)
#               informer_id=getUserID(informer)
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


def bulkInsertSpot(informer_id,longitude,latitude,qty) :
        lconn = g_pool.getconn()
        cur = lconn.cursor() 
        try:
            cur.execute("INSERT INTO huhula.spots(informer_id,informed_at,azimuth,altitude,longitude,latitude,direction,quantity,orig_quantity,client_at,mode) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (informer_id,int(round(time.time() * 1000)),0,0.156,longitude,latitude,[-3],qty,qty,int(round(time.time() * 1000)),2))
            lconn.commit()
            return 0            
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
