import json
import psycopg2
import time

def openConn() :
    global conn
    global cur
    conn = psycopg2.connect(database="huhula", user="root", host="roachdb", port=26257)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

openConn()

def getUserID(user) :
    cur.execute("SELECT id FROM users WHERE userhash = '" + user + "'")
    return cur.fetchone()[0] 

print getUserID("strix")

def newUser(user) :
        cur.execute("INSERT INTO huhula.users(userhash) values(%s)",(user,))

def insertSpot(informer,informed_at,azimuth,altitude,longitude,latitude,spot,client_at) :
        informer_id=getUserID(informer)
        if ( informer_id is None ) :
                newUser(informer)
                informer_id=getUserID(informer)

        cur.execute("INSERT INTO huhula.spots(informer_id,informed_at,azimuth,altitude,longitude,latitude,spot,client_at) values(%s,%s,%s,%s,%s,%s,%s,%s)",
            (informer_id,informed_at,azimuth,altitude,longitude,latitude,spot,client_at))

insertSpot("strix",45,3.456,5.23,3.45,6.78,0,12345689)

cur.close()
conn.close()

