#!flask/bin/python

import spot_db

import logging, logging.config, yaml
logging.config.dictConfig(yaml.load(open('logging.conf')))
logfl    = logging.getLogger('file')
logconsole = logging.getLogger('console')
logfl.debug("Debug FILE")
logconsole.debug("Debug CONSOLE")

def calc_balance(user,dfrom,dto):
    logconsole.info("start calc balance for "+user+" dfrom="+str(dfrom)+" dto="+str(dto))
    uid = spot_db.getUserID(user)
    informed = spot_db.getInformedSpots(uid,dfrom,dto)
    mnat = None
    mxat = None
    if informed == None:
        informed_qty = 0
        mnat = dfrom
        mxat = dto
    else:
        informed_qty = informed[0]
        mnat = informed[2]
        mxat = informed[3]
    occupied = spot_db.getOccupiedSpots(uid,mnat,mxat)
    if occupied == None:
        occupied_qty = 0
    else:
        occupied_qty = occupied[0]
    logconsole.info("user="+user+"; dfrom="+str(dfrom)+"; dto="+str(dto)+" informed_qty="+str(informed_qty)+" occupied_qty="+str(occupied_qty))
    logconsole.info("end calc balance for "+user+" dfrom="+str(dfrom)+" dto="+str(dto))
    return (user,uid,mnat,mxat,informed_qty,occupied_qty)

