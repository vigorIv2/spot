import json
import psycopg2
import time
from random import choice
from string import ascii_uppercase, ascii_lowercase, digits

def randomString() : 
    return "test"+''.join(choice(ascii_uppercase+ascii_lowercase+digits) for i in range(25))
 
def openConn() :
    global conn
    global cur
#    conn = psycopg2.connect(database="huhula", user="root", host="roachdb", port=26257)
#    cs="postgresql://huhuladb00:26257/mydb?user=root&sslcert=/Users/ivasilchikov/spot/certs/client.root.crt&sslkey=/Users/ivasilchikov/spot/certs/client.root.key&sslmode=require&ssl=true"
    cs="postgresql://huhuladb00:26257/huhula?user=huhulaman&password=sEBx9gjgzfo&sslcert=/Users/ivasilchikov/spot/certs/client.huhulaman.crt&sslkey=/Users/ivasilchikov/spot/certs/client.huhulaman.key&sslmode=require&ssl=true"
    conn = psycopg2.connect(cs)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    cur.execute("show databases;")
    res=cur.fetchall()
    print "res="+str(res) 
    
openConn()

def getUserID(user) :
    cur.execute("SELECT id FROM users WHERE userhash = '" + user + "'")
    return cur.fetchone()[0] 

print getUserID("strix")

print randomString()

def newUser(user) :
	print("creating user "+user) 
        cur.execute("INSERT INTO huhula.users(userhash) values(%s)",(user,))

def insertSpot(informer,informed_at,azimuth,altitude,longitude,latitude,spot,client_at) :
        informer_id=getUserID(informer)
        if ( informer_id is None ) :
                newUser(informer)
                informer_id=getUserID(informer)

        cur.execute("INSERT INTO huhula.spots(informer_id,informed_at,azimuth,altitude,longitude,latitude,spot,client_at) values(%s,%s,%s,%s,%s,%s,%s,%s)",
            (informer_id,informed_at,azimuth,altitude,longitude,latitude,spot,client_at))

cur.close()
conn.close()

