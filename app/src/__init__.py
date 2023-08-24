from fastapi import HTTPException
from datetime import datetime
from dateutil import parser
from calendar import timegm
from config import configs as p
import uuid, base64, time, pandas, requests, json, app.logs as log

def requestsApi(method, url, body=None, headers={}, verify=p.IS_TLS_ENABLE, timeout=p.IS_TLS_TIME_LIMIT):

    try:
        if body is not None and not isinstance(body, dict):
            body = json.loads(body)
        r = requests.request(method, url, json=body, timeout=timeout, headers=headers, verify=verify)
        res = json.loads(r.text)
        r_status = r.status_code
        #log.sys_log.info(f"[REQ] url res: {res}")
    except Exception as e:
        res = e
        r_status = 500
        log.sys_log.error(f"[REQ] url res: {e}, {url}")
        raise HTTPException(status_code=409, detail=f"This name:{type} already exists.")
    finally:
        return res, r_status

def convertTimeToStr(dt: datetime):  
    if dt.utcoffset() is not None:
        raise ValueError('system does not support timezone')
    return dt.isoformat(timespec='milliseconds')+"Z"

def convertStrToTime(dt: str):
    return parser.parse(dt)

def convertTimeToMs(timestamp):
    try:
        return 1000 * timegm(datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').timetuple())
    except:
        return 1000 * timegm(datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ').timetuple())

def unixtime():
    now = datetime.utcnow()
    return time.mktime(now.timetuple())*1000
    
def uuidGenerator(prefix, suffix):
    pid = uuid.uuid4()
    pid = pid.hex
    pid = prefix+pid[:6]+"."+suffix+pid[7:23]
    return pid

def strTimeProp(start, end, prop, frmt):
    stime = time.mktime(time.strptime(start, frmt))
    etime = time.mktime(time.strptime(end, frmt))
    ptime = stime + prop * (etime - stime)
    return int(ptime)

def allowedFile(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1] in ['zip']

def identifyHeader(file_name, file):
    try:
        data = pandas.read_csv(file,encoding='ISO-8859-1')
        #log.sys_log.info("[CHECK] csv file has no header: {}".format(file_name))
        return False, data    
    except:
        log.sys_log.info("[CHECK] csv file has header: {}".format(file_name))
        return True, None

def changeID(objextid, modelName = "Parameter"):
    objextid = str(objextid)
    try:
        modelName = bytes(modelName, 'utf-8')
        modelName = bytes.decode(base64.urlsafe_b64encode(modelName).strip(b'='))
        objextid = objextid.split("_")
        objextid = objextid[-1]
        objextid = bytes.fromhex(objextid)
        objextid = bytes.decode(base64.urlsafe_b64encode(objextid))
        nodeId = modelName+"."+objextid
        return nodeId
    except Exception as e :                                      
        log.sys_log.error("[CHECK] convert _id: {}".format(e))
        return None

def reChangeID(objextid):
    try:
        objextid = objextid.split(".")
        objextid = objextid[-1]
        encoded3 = base64.urlsafe_b64decode(objextid).hex()
        return encoded3
    except Exception as e :                                      
        log.sys_log.error("[CHECK] convert _id: {}".format(e))
        return None