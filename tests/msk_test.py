import logging
import sys
import time
import datetime
import unittest
import spot_db
from spot_msk import SpotMsk
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
    def setUpClass(self):
        self._started_at = time.time()
        self._total_steps_cnt = 0
        self._total_steps_elapsed = 0
        self.msk = SpotMsk()

        logging.info('executing setUpClass')

    def test_00_msk_parking(self):
        self.msk.get_datasets()

    def test_01_msk_622(self):
        self.msk.traverse_dataset(622)

    def test_01_parking_datasets(self):
        dss = self.msk.get_datasets()
        cnt = 0
        for ds in sorted(dss):
            cnt += self.msk.traverse_dataset(ds)
        logging.info('total datasets '+str(cnt))

    @classmethod
    def tearDownClass(self):
        logging.info('executing tearDownClass')
        self._step_started_at = time.time()
        elapsed = time.time() - self._started_at
        elapsed_step = time.time() - self._step_started_at
        self._total_steps_cnt += 1.0
        self._total_steps_elapsed += elapsed_step
        avg_elapsed = self._total_steps_elapsed / self._total_steps_cnt
        logging.info("total_elapsed=" + str(round(elapsed, 2)) + " step_elapsed=" + str(round(elapsed_step, 2)) + " avg_elapsed=" + str(round(avg_elapsed, 2)))

        logging.info('executed tearDownClass')

if __name__ == '__main__':
    unittest.main()
