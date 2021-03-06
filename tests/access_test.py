import logging
import sys
import time
import datetime
import unittest
import spot_db
import spot_billing
import json, requests

import logging, logging.config, yaml
logging.config.dictConfig(yaml.load(open('logging.conf')))
logfl    = logging.getLogger('file')
logconsole = logging.getLogger('console')
logfl.debug("Debug FILE")
logconsole.debug("Debug CONSOLE")


class TestAccess(unittest.TestCase):

    def echo_elapsed_time(self):
        elapsed = time.time() - self._started_at
        elapsed_step = time.time() - self._step_started_at
        self._total_steps_cnt += 1.0
        self._total_steps_elapsed += elapsed_step
        avg_elapsed = self._total_steps_elapsed / self._total_steps_cnt
        logging.info("total_elapsed=" + str(round(elapsed, 2)) + " step_elapsed=" + str(round(elapsed_step, 2)) + " avg_elapsed=" + str(round(avg_elapsed, 2)))


    def echo(self,r):
        logging.info("response=" + str(r))
        logging.info("response.headers=" + str(r.headers))
        logging.info("response.text=" + str(r.text))
        self.echo_elapsed_time()
        
    @classmethod
    def isIntranet(self):
        return urls[0].startswith("http://192.")

    @classmethod
    def setUpClass(self):
        global test_users
        global test_coord  
        test_coord = [ 
                       [ 59.572485, 150.810362 ],
                       [ 59.582485, 150.710362 ],
                       [ 59.592485, 150.610362 ],
                       [ 59.692485, 151.610362 ],
                       [ 79.692485, 141.610362 ]
                     ]   
                              
        self._started_at = time.time()
        self._total_steps_cnt = 0
        self._total_steps_elapsed = 0

        test_users = ['unittest', 'unittest01', 'unittest02', 'unittest03']
        logging.info('executing setUpClass')
        if self.isIntranet():
            spot_db.cleanUp(test_users)
        logging.info("URLs to check "+str(urls))

    def postit(self,url,payload):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        logging.info("checking url="+url+" headers="+str(headers)+" payload="+str(payload)) 
        response = requests.post(url, auth = ('testuser', 'python'), json = payload, headers = headers, verify=False)
        self.echo( response )
        return response

    def test_00_register(self):
        for u in test_users:
            self._step_started_at = time.time()
            payload = {"id":u}
            for ur in urls:
                r = self.postit( ur + "/spot/api/v1.0/register", payload )
                self.assertTrue( r.status_code == 201 )

    def test_01_locate(self):
        payload = {"uid":"unittest01","loc":{"lt":33.637871,"lg":-117.739564,"al":-1}}
        for ur in urls:
            self._step_started_at = time.time()
            r = self.postit( ur + "/spot/api/v1.0/locate", payload )
            self.assertTrue( r.status_code == 200 )

    def test_02_park(self):
        payload = {"uid":"unittest01","ct":"12345", "deg":"10", "loc":{"lt":59.572485,"lg":150.810362,"al":-1}}
        for ur in urls:
            self._step_started_at = time.time()
            r = self.postit( ur + "/spot/api/v1.0/park", payload )
            self.assertTrue( r.status_code == 201 )

    def test_03_spot(self):
        qty = 0
        ur = urls[-1]
        for sp in test_coord:
            self._step_started_at = time.time()
            qty += 3
            payload = {"uid": "unittest02", "ct":"12345", "deg":"10", "q":qty, "spot":[-2], "loc":{"lt":sp[0], "lg":sp[1], "al":-1}}
            r = self.postit( ur + "/spot/api/v1.0/spot", payload )
            self.assertTrue( r.status_code == 201 ) 

    def test_04_take(self):
        for u in test_users:
            for sp in test_coord:
                self._step_started_at = time.time()
                logging.info("sp="+str(sp))
                payload = {"uid":u, "ct":"12345", "deg":"10", "spot":[0,1], "loc":{"lt":sp[0], "lg":sp[1], "al":0}}
                ur = urls[-1]
                r = self.postit( ur + "/spot/api/v1.0/spot", payload )
                self.assertTrue( r.status_code == 201 )
                payload2 = {"uid":"unittest03","loc":{"lt":sp[0],"lg":sp[1],"al":-1}}
                r2 = self.postit( ur + "/spot/api/v1.0/locate", payload2 )
                self.assertTrue( r2.status_code == 200 )
                jsid = json.loads(r2.text)
                sid = jsid["spots"][0]["sid"]
                logging.info("occupying sid="+str(sid))
                payload3 = {"uid":"unittest03","ct":"4321","sid":sid,"loc":{"lt":sp[0],"lg":sp[1]}}
                r3 = self.postit( ur + "/spot/api/v1.0/take", payload3 )
                self.assertTrue( r3.status_code == 201 )

    def test_05_last_day(self):
        self.assertTrue(spot_db.last_day_of_month(datetime.datetime.strptime("2018-01-22", "%Y-%m-%d").date()) == "2018-01-31")
        self.assertTrue(spot_db.last_day_of_month(datetime.datetime.strptime("2018-02-02", "%Y-%m-%d").date()) == "2018-02-28")
        self.assertTrue(spot_db.last_day_of_month(datetime.datetime.strptime("2018-03-29", "%Y-%m-%d").date()) == "2018-03-31")
        self.assertTrue(spot_db.last_day_of_month(datetime.datetime.strptime("2018-04-01", "%Y-%m-%d").date()) == "2018-04-30")
        self.assertTrue(spot_db.last_day_of_month(datetime.datetime.strptime("2018-05-11", "%Y-%m-%d").date()) == "2018-05-31")
        self.assertTrue(spot_db.last_day_of_month(datetime.datetime.strptime("2018-06-21", "%Y-%m-%d").date()) == "2018-06-30")
        self.assertTrue(spot_db.last_day_of_month(datetime.datetime.strptime("2018-07-21", "%Y-%m-%d").date()) == "2018-07-31")
        self.assertTrue(spot_db.last_day_of_month(datetime.datetime.strptime("2018-08-21", "%Y-%m-%d").date()) == "2018-08-31")
        self.assertTrue(spot_db.last_day_of_month(datetime.datetime.strptime("2018-09-21", "%Y-%m-%d").date()) == "2018-09-30")
        self.assertTrue(spot_db.last_day_of_month(datetime.datetime.strptime("2018-10-21", "%Y-%m-%d").date()) == "2018-10-31")
        self.assertTrue(spot_db.last_day_of_month(datetime.datetime.strptime("2018-11-21", "%Y-%m-%d").date()) == "2018-11-30")
        self.assertTrue(spot_db.last_day_of_month(datetime.datetime.strptime("2018-12-21", "%Y-%m-%d").date()) == "2018-12-31")

    def test_06_check_balance(self):
        for ur in urls:
            for u in test_users:
                self._step_started_at = time.time()
                payload = {"id": u}
                r = self.postit( ur + "/spot/api/v1.0/balance", payload )
                self.assertTrue( r.status_code == 201 ) 


    def test_07_referral(self):
	pu = None	
        for u in test_users:
            self._step_started_at = time.time()
            payload = {"id":u}
            for ur in urls:
                r = self.postit( ur + "/spot/api/v1.0/refer", payload )
                self.assertTrue( r.status_code == 201 )
                refjson = json.loads(r.text)
                rid = refjson["reference"]["ref"]
                r = self.postit( ur + "/spot/api/v1.0/register", payload )
                self.assertTrue( r.status_code == 201 )
		regjson = json.loads(r.text)
		self.assertTrue( "user" in regjson )
		self.assertTrue( "created_at" in regjson["user"] )
		self.assertTrue( "id" in regjson["user"] )
		self.assertTrue( "roles" in regjson["user"] )
		if pu != None:
			npayload = payload
			npayload['ref'] = rid	
			npayload['id'] = pu # previous user to avoud refering yourself
			logging.info("refering "+str(npayload))
                	r = self.postit( ur + "/spot/api/v1.0/register", npayload )
                	self.assertTrue( r.status_code == 201 )
	    pu = u

    def test_08_double_referral(self):
        self._step_started_at = time.time()
        payload = {"id":test_users[1]}
        for ur in urls:
            r = self.postit( ur + "/spot/api/v1.0/refer", payload )
            self.assertTrue( r.status_code == 201 )
            refjson = json.loads(r.text)
            rid = refjson["reference"]["ref"]
            npayload = payload
	    npayload['ref'] = rid	
	    npayload['id'] = test_users[2] # previous user to avoid refering yourself
	    logging.info("refering "+str(npayload))
            r = self.postit( ur + "/spot/api/v1.0/register", npayload )
            self.assertTrue( r.status_code == 201 )
            r = self.postit( ur + "/spot/api/v1.0/register", npayload )
            self.assertTrue( r.status_code == 201 )

    def test_09_referral(self):
	pu = None	
        for u in test_users:
            self._step_started_at = time.time()
            payload = {"id":u,"links":[u+"_bro1",u+"_bro2"]}
            for ur in urls:
                r = self.postit( ur + "/spot/api/v1.0/referral", payload )
                print "refer status code "+str(r.status_code) 
                self.assertTrue( r.status_code == 201 )
                refjson = json.loads(r.text)
                rid = refjson["referral"]["ref"]
                payload = {"id":u,"ref":rid}
                r = self.postit( ur + "/spot/api/v1.0/register", payload )
                self.assertTrue( r.status_code == 201 )
		regjson = json.loads(r.text)
		self.assertTrue( "user" in regjson )
		self.assertTrue( "created_at" in regjson["user"] )
		self.assertTrue( "id" in regjson["user"] )
		self.assertTrue( "roles" in regjson["user"] )
		if pu != None:
			npayload = payload
			npayload['ref'] = rid	
			npayload['id'] = pu # previous user to avoid refering yourself
			logging.info("refering "+str(npayload))
                	r = self.postit( ur + "/spot/api/v1.0/register", npayload )
                	self.assertTrue( r.status_code == 201 )
	    pu = u


#
# urrently billing calculate on the fly 
#    def test_15_bill(self):
#        if self.isIntranet():
#            self._step_started_at = time.time()
#            (user,uid,mnat,mxat,informed_qty,occupied_qty)=spot_billing.calc_balance('unittest','2018-01-01 00:00:00','2018-12-31 00:00:00')
#            self.assertTrue( informed_qty == 10 )
#            (user,uid,mnat,mxat,informed_qty,occupied_qty)=spot_billing.calc_balance('unittest01','2018-01-01 00:00:00','2018-12-31 00:00:00')
#            self.assertTrue( informed_qty == 10 )
#            (user,uid,mnat,mxat,informed_qty,occupied_qty)=spot_billing.calc_balance('unittest02','2018-01-01 00:00:00','2018-12-31 00:00:00')
#            self.assertTrue( informed_qty == 55 )
#            (user,uid,mnat,mxat,informed_qty,occupied_qty)=spot_billing.calc_balance('unittest03','2018-01-01 00:00:00','2018-12-31 00:00:00')
#            self.assertTrue( informed_qty == 10 )
#            self.assertTrue( occupied_qty == 4 )
#
#    def test_16_save_bill(self):
#        if self.isIntranet():
#            self._step_started_at = time.time()
#            for u in test_users:
#                spot_billing.do_billing(u,'2018-01-01 00:00:00','2018-12-31 00:00:00')
#

    @classmethod
    def tearDownClass(self):
        logging.info('executing tearDownClass')
        self._step_started_at = time.time()
        if self.isIntranet():
            spot_db.cleanUp(test_users)

#        self.echo_elapsed_time()
        elapsed = time.time() - self._started_at
        elapsed_step = time.time() - self._step_started_at
        self._total_steps_cnt += 1.0
        self._total_steps_elapsed += elapsed_step
        avg_elapsed = self._total_steps_elapsed / self._total_steps_cnt
        logging.info("total_elapsed=" + str(round(elapsed, 2)) + " step_elapsed=" + str(round(elapsed_step, 2)) + " avg_elapsed=" + str(round(avg_elapsed, 2)))

        logging.info('executed tearDownClass')

if __name__ == '__main__':
    global urls
    urls = sys.argv[1:]
    while len(sys.argv) > 1:
        del(sys.argv[1])
    print "URLs to check "+str(urls)
    unittest.main()
