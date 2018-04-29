import json
import psycopg2
import requests
import time

conn = psycopg2.connect(database="huhula", user="root", host="roachdb", port=26257)
conn.set_session(autocommit=True)
cur = conn.cursor()

data=[]
cur.execute("""INSERT INTO huhula.spots(informer_id,informed_at,azimuth,altitude,longitude,latitude,spots) values('e732e330-ad88-4e28-bd94-70e0cedb9952',12345,123.45678,1.23,3.45,6.78,'[0,2,3]')""")
# insert into huhula.spots(informer_id,informed_at,azimuth,altitude,longitude,latitude,spots) values('e732e330-ad88-4e28-bd94-70e0cedb9952',12345,123.45678,1.23,3.45,6.78,'[0,2,3]');

cur.close()
conn.close()

