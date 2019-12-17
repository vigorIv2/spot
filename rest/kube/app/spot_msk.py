#!flask/bin/python
# -*- coding: utf-8 -*-

import logging
import traceback
import sys
import time
import datetime
import unittest
import spot_db
import json, requests

import logging, logging.config, yaml
logging.config.dictConfig(yaml.load(open('logging.conf')))
logfl    = logging.getLogger('file')
logconsole = logging.getLogger('console')
logfl.debug("Debug FILE")
logconsole.debug("Debug CONSOLE")


class SpotMsk():

    def __init__(self):
        self.url = "https://apidata.mos.ru"
        self.api_key = "06cbca96b6efa408b5a061a4a17d143d"
        self._started_at = time.time()
        self._step_started_at = time.time()
        self._total_steps_cnt = 0
        self._total_steps_elapsed = 0

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
        logging.info("response.text=" + str(r.text.encode("utf-8")))
        self.echo_elapsed_time()
        
    def postit(self,url,payload):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        logging.info("calling opendata api url="+url+" headers="+str(headers)+" payload="+str(payload)) 
        response = requests.post(url, json = payload, headers = headers) #, verify=False)
        self.echo( response )
        return response

    def saveDataset(self,informer_id,lat,lon,capacity):
        spot_db.bulkInsertSpot(informer_id,lon,lat,capacity) 

    def traverse_dataset(self,dsid,func = None):
        self._step_started_at = time.time()
        cnt = 0 
        npcnt = 0
        informer_id = spot_db.getUserID("strix") # rerpot as huhulaspot
        try:
            payload = {}
            r = self.postit( self.url + "/v1/features/%s?api_key=%s" % (dsid, self.api_key), payload )
            jlst = json.loads(r.text)
            for jj in jlst["features"]:
                capacity = str(jj["properties"]["Attributes"].get("CarCapacity", "0")).replace("null","1")
                if capacity == None or capacity == "None":
                    capacity = 0
                name = jj["properties"]["Attributes"].get("ParkingName", "not")
                tpe = jj["geometry"].get("type","")
                if tpe == "Point":
                    coord = jj["geometry"]["coordinates"]
                elif tpe == "MultiLineString":
                    coord = jj["geometry"]["coordinates"][0][0]
                if name == "not" or capacity == 0 or len(coord) != 2:
                    npcnt += 1
                    continue
                lat = coord[1]
                lon = coord[0]
                attr = jj["properties"]["Attributes"]
                meter = jj["properties"]["Attributes"].get("NumberOfParkingMeter","0")
                phone = jj["properties"]["Attributes"].get("OrgPhone", "")
                district = jj["properties"]["Attributes"].get("District", "")
#                description = jj["properties"]["Attributes"].get("LocationDescription", "")
#                area = jj["properties"]["Attributes"].get("AdmArea", "")
                cnt += 1
                logging.info("dsid="+str(dsid)+"; lat="+str(lat)+"; lon="+str(lon)+"; name="+name+"; capacity="+str(capacity)+" meter="+str(meter))
                if func != None:
                    func(informer_id,lat,lon,capacity)
        except Exception as error:
            jts = traceback.format_exc()
            logconsole.error(jts)
        logging.info("dataset "+str(dsid)+"; element count = "+str(cnt)+" not a parking cnt="+str(npcnt))
        time.sleep(3)
        return cnt

    def get_datasets(self):
        self._step_started_at = time.time()
        cnt = 0 
        try:
            payload = {}
            r = self.postit( self.url + "/v1/categories/13?api_key=%s" % (self.api_key), payload )
            jlst = json.loads(r.text)
            datasets = []
            for dsid in jlst["Datasets"]:
                if dsid in [60733,60508,60730]:
                    logging.info("skipping dsid="+str(dsid)+"; it throws 500 on server side")
                    continue
                datasets.append(dsid)
                logging.info("dsid="+str(dsid))
        except Exception as error:
            jts = traceback.format_exc()
            logconsole.error(jts)

        logging.info("element count = "+str(cnt))
        return datasets 
       

    def update_datasets(self):
        dss = self.get_datasets()
        cnt = 0
        for ds in sorted(dss):
            cnt += self.traverse_dataset(ds,self.saveDataset)
        logging.info('total datasets updated '+str(cnt))

if __name__ == '__main__':
    msk = SpotMsk()
    msk.update_datasets()

