import logging
import sys
import time
import unittest
import spot_db
import json, requests

import logging, logging.config, yaml
logging.config.dictConfig(yaml.load(open('logging.conf')))
logfl    = logging.getLogger('file')
logconsole = logging.getLogger('console')
logfl.debug("Debug FILE")
logconsole.debug("Debug CONSOLE")


class TestAccess(unittest.TestCase):

    def echo(self,r):
        elapsed = time.time() - self._started_at
        elapsed_step = time.time() - self._step_started_at
        logging.info("response=" + str(r))
        logging.info("response.headers=" + str(r.headers))
        logging.info("response.text=" + str(r.text))
        logging.info("total_elapsed=" + str(round(elapsed, 2)) + " step_elapsed=" + str(round(elapsed_step, 2)))

    @classmethod
    def setUpClass(self):
        global test_users
        global test_coord  
        test_coord = [ 
                       [ 59.572485, 150.810362 ],
                       [ 59.572485, 150.810362 ],
                       [ 59.572485, 150.810362 ]
                     ]   
                              
        self._started_at = time.time()
        test_users = ['unittest', 'unittest01', 'unittest02', 'unittest03']
        logging.info('executing setUpClass')
        con = spot_db.openConn()
        spot_db.cleanUp(test_users)
        spot_db.cur.close()
        spot_db.conn.close()
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
        self._step_started_at = time.time()
        payload = {"uid":"unittest01","loc":{"lt":33.637871,"lg":-117.739564,"al":-1}}
        for ur in urls:
            r = self.postit( ur + "/spot/api/v1.0/locate", payload )
            self.assertTrue( r.status_code == 200 )

    def test_02_park(self):
        self._step_started_at = time.time()
        payload = {"uid":"unittest01","ct":"12345", "deg":"10", "loc":{"lt":59.572485,"lg":150.810362,"al":-1}}
        for ur in urls:
            r = self.postit( ur + "/spot/api/v1.0/park", payload )
            self.assertTrue( r.status_code == 201 )

    def test_03_spot(self):
        self._step_started_at = time.time()
        payload = {"uid":"unittest03","ct":"12345", "deg":"10", "spot":[0,1], "loc":{"lt":59.572485,"lg":150.810362,"al":-1}}
        ur = urls[-1]
        r = self.postit( ur + "/spot/api/v1.0/spot", payload )
        self.assertTrue( r.status_code == 201 ) 

    @classmethod
    def tearDownClass(self):
        logging.info('executing tearDownClass')
        self._step_started_at = time.time()
        con = spot_db.openConn()
        spot_db.cleanUp(test_users)
        spot_db.cur.close()
        spot_db.conn.close()
        elapsed = time.time() - self._started_at
        elapsed_step = time.time() - self._step_started_at
        logging.info("total_elapsed=" + str(round(elapsed, 2)) + " step_elapsed=" + str(round(elapsed_step, 2)))

        logging.info('executed tearDownClass')

if __name__ == '__main__':
    global urls
    urls = sys.argv[1:]
    while len(sys.argv) > 1:
        del(sys.argv[1])
    print "URLs to check "+str(urls)
    unittest.main()
