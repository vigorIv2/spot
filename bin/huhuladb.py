import json
import psycopg2
import requests
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

def insertSpot(informer,informed_at,azimuth,altitude,longitude,latitude,spots) :
    informer_id=getUserID("strix")
    cur.execute("INSERT INTO huhula.spots(informer_id,informed_at,azimuth,altitude,longitude,latitude,spots) values(%s,%s,%s,%s,%s,%s,%s)",
            (informer_id,informed_at,azimuth,altitude,longitude,latitude,spots))

insertSpot("strix",45,3.456,5.23,3.45,6.78,'[0,2,3]')

cur.close()
conn.close()

