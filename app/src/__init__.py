import uuid, base64, time, pandas, requests, json, app.logs as log, app.database as db, pandas as pd
from fastapi import HTTPException
from datetime import datetime, timedelta
from dateutil import parser
from calendar import timegm
from config import configs as p

InfluxDB = db.InfluxDB()

def requestsApi(method, url, body=None, headers={}, verify=p.SKIP_TLS, timeout=p.IFPS_TIME_OUT):

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

def getTenantList():
    try:
        query = {
            "query": "query allTenants { allTenants { id name } } ",
        }
        r = requests.post(p.IFP_DESK_API_URL, json=query, headers = getEnSaaSSecret(), verify=p.SKIP_TLS)

        res = json.loads(r.text)

        if "errors" in res:
            return None

        tenantlist = res.get("data").get("allTenants")

        if tenantlist is None:
            tenantlist = []

        return tenantlist
    except Exception as e:
        log.sys_log.error("- Get All Tenant: {}.".format(e))
        return None

def getEnSaaSSecret():
    
    ### 正式上線用 ### 
    cs = p.clientSecrets.get(f'{p.IAPP_NAME}')
    if cs is not None:
        cs_app = cs.get(f'{p.IAPP_NAME}')
        if cs_app is not None:
            log.sys_log.info(f"[GCS] X-Ifp-App-Secret:{cs_app},X-Ifp-Service-Name:{p.IAPP_NAME}")
            return {"X-Ifp-App-Secret":cs_app,"X-Ifp-Service-Name":p.IAPP_NAME}

    ### 開發用 ###
    res, r_status = requestsApi("GET", f"{p.IFPS_ETCD_BROKER_API_URL}/service")
    if (r_status == requests.codes.ok):
        if "X-Ifp-Service-Name" in res:
            return res
    log.sys_log.error(f"[GCS] Get ensaas secret failed {p.IFPS_ETCD_BROKER_API_URL}, body - {res}")
    return {}

def getEanSecret():

    ### 正式上線用 ### 
    cs = p.clientSecrets.get(f'{p.IAPP_NAME}')
    if cs is not None:
        cs_app = cs.get(f'ifp-ean')
        if cs_app is not None:
            log.sys_log.info(f"[GCS] X-Ifp-App-Secret:{cs_app},X-Ifp-Service-Name:EAN")
            return {"X-Ifp-App-Secret":cs_app,"X-Ifp-Service-Name":"EAN"}

    ### 開發用 ###
    res, r_status = requestsApi("GET", f"{p.IFPS_ETCD_BROKER_API_URL}/service/ean")
    if (r_status == requests.codes.ok):
        if "X-Ifp-Service-Name" in res:
            return res
    log.sys_log.error(f"[GCS] Get ean secret failed {p.IFPS_ETCD_BROKER_API_URL}, body - {res}")
    return {}

def getMobileSecret():
    
    ### 正式上線用 ### 
    cs = p.clientSecrets.get(f'{p.IAPP_NAME}')
    if cs is not None:
        cs_app = cs.get(f'imobile-services')
        if cs_app is not None:
            log.sys_log.info(f"[GCS] X-Ifp-App-Secret:{cs_app},X-Ifp-Service-Name:iMobile")
            return {"X-Ifp-App-Secret":cs_app,"X-Ifp-Service-Name":"iMobile"}
            
    ### 開發用 ###
    res, r_status = requestsApi("GET", f"{p.IFPS_ETCD_BROKER_API_URL}/service/imobile")
    if (r_status == requests.codes.ok):
        if "X-Ifp-Service-Name" in res:
            return res
    log.sys_log.error(f"[GCS] Get imobile secret failed {p.IFPS_ETCD_BROKER_API_URL}, body - {res}")
    return {}

def getMaintenanceSecret():
    
    ### 正式上線用 ### 
    cs = p.clientSecrets.get(f'{p.IAPP_NAME}')
    if cs is not None:
        cs_app = cs.get(f'Maintenance')
        if cs_app is not None:
            log.sys_log.info(f"[GCS] X-Ifp-App-Secret:{cs_app},X-Ifp-Service-Name:Maintenance")
            return {"X-Ifp-App-Secret":cs_app,"X-Ifp-Service-Name":"Maintenance"}
            
    ### 開發用 ###
    res, r_status = requestsApi("GET", f"{p.IFPS_ETCD_BROKER_API_URL}/service/maintenance")
    if (r_status == requests.codes.ok):
        if "X-Ifp-Service-Name" in res:
            return res
    log.sys_log.error(f"[GCS] Get maintenance secret failed {p.IFPS_ETCD_BROKER_API_URL}, body - {res}")
    return {}

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

def get_machine_detail(machineId, tenantId):
    
    query = {
        "query": "query machine($id: ID!) { machine(id: $id) { id name parameters(first: 100){ nodes{ name scadaId tagId }}}}",
        "variables": {"id": machineId},
    }

    headers = getEnSaaSSecret()
    if tenantId is not None and p.IFP_DESK_PREFIX != "ifp-organizer":
        headers["X-Ifp-Tenant-Id"] = tenantId

    res, r_status = requestsApi("POST", f"{p.IFP_DESK_API_URL}", query, headers)
    try:
        if res.get('errors') is not None: 
            return None
        res = res.get('data').get('machine').get('parameters').get('nodes')
        if res[0]is None :
            return None
        response = []
        for r in res:
            if r.get('tagId') is not None:
                response.append(r)
        return response
    except Exception as e:
        log.sys_log.error(f"[CHECK] get machine detail: {e}")

def get_machine_info(machineId, tenantId):
    
    query = {
        "query": "query machine($id: ID!) { machine(id: $id) { id name parameters(first: 100){ nodes{ name scadaId tagId }}}}",
        "variables": {"id": machineId},
    }

    headers = getEnSaaSSecret()
    if tenantId is not None and p.IFP_DESK_PREFIX != "ifp-organizer":
        headers["X-Ifp-Tenant-Id"] = tenantId

    res, r_status = requestsApi("POST", f"{p.IFP_DESK_API_URL}", query, headers)
    if res.get('errors') is not None: return None

    deviceName = res.get("data").get("machine").get("name")
    deviceInfo = res.get("data").get("machine")
    
    return deviceName, deviceInfo

def get_parameters_info(parameterlist, tenantId=None, taskName= None):
    
    query = {
        "query": "query parametersByIds($ids: [ID!]!){ parametersByIds(ids: $ids){ id name scadaId tagId machine{ group{ id name tenantId } id name}}}",
        "variables": { "ids":parameterlist},
    }

    headers = getEnSaaSSecret()
    if tenantId is not None and p.IFP_DESK_PREFIX != "ifp-organizer":
        headers["X-Ifp-Tenant-Id"] = tenantId

    res, r_status = requestsApi("POST", f"{p.IFP_DESK_API_URL}", query, headers)
    if res.get("errors") is not None: return []

    dictList = res.get("data").get("parametersByIds")

    return dictList

def get_influx_data(sourceData, fromTime="2023-03-01T00:00:00Z", toTime="2023-04-31T00:00:00Z", limit=None):
    
    for res in sourceData:
        scadaId = res.get("scadaId")
        tagId   = res.get("tagId")
        kind    = res.get("kind")
    
    toTime = convertTimeToStr(datetime.utcnow())
    fromTime = convertTimeToStr(datetime.utcnow()-timedelta(days=7))
    if scadaId is not None and tagId is not None and kind is None and limit is None:
        execute = f"""select time,num from tag_value.tag_value  WHERE scada ='{scadaId}' AND "tag"='{tagId}' AND time >= '{fromTime}' AND time <= '{toTime}' ORDER BY time ASC """
    elif scadaId is not None and tagId is not None and kind is None and limit is not None:
        execute = f"""select time,num from tag_value.tag_value  WHERE scada ='{scadaId}' AND "tag"='{tagId}' ORDER BY time ASC limit {limit} """
    else:
        return []
    log.sys_log.error(f"[PHM] infulx execute: {execute}.")
    results = InfluxDB.selectSql(execute)
    if len(list(results)) == 0:
        return None
    df = pd.DataFrame.from_dict(list(results)[0], orient='columns')
    resp = df.values.tolist()
    df = pd.DataFrame (resp, columns = ['time', 'num'])
    return df

def get_influx_data_new(source_data_list, from_time=None, to_time=None, limit=None):
    """
    從 InfluxDB 中取得資料，依據傳入的 source_data_list 來查詢對應的資料。
    Args:
        source_data_list (List[Dict]): 包含 scadaId、tagId、kind 的資料列表
        from_time (str): 起始時間，預設為七天前
        to_time (str): 結束時間，預設為現在
        limit (int): 取得資料的數量限制，預設為不限制

    Returns:
        pd.DataFrame: 取得的 InfluxDB 資料
    """
    if from_time is None:
        to_time = convertTimeToStr(datetime.utcnow())
        from_time = convertTimeToStr(datetime.utcnow() - timedelta(days=7))

    execute_list = []
    for source_data in source_data_list:
        scada_id = source_data.get("scadaId")
        tag_id = source_data.get("tagId")
        kind = source_data.get("kind")
        if scada_id is None or tag_id is None:
            continue

        if kind is None and limit is None:
            execute = f"""select * from tag_value.tag_value  WHERE scada ='{scada_id}' AND "tag"='{tag_id}' AND time >= '{from_time}' AND time <= '{to_time}' ORDER BY time ASC """
        elif kind is None and limit is not None:
            execute = f"""select time,num from tag_value.tag_value  WHERE scada ='{scada_id}' AND "tag"='{tag_id}' ORDER BY time ASC limit {limit} """
        else:
            continue

        execute_list.append(execute)

    if not execute_list:
        return pd.DataFrame()

    execute_str = ";".join(execute_list)
    log.sys_log.info(f"[PHM] Influx execute: {execute_str}.")
    results = InfluxDB.selectSql(execute_str)

    if not results:
        return pd.DataFrame()

    results_list = []
    for result_set in results:
        for series_key in result_set.keys():
            result_list = result_set[series_key]
            results_list.extend(result_list)

    df = pd.DataFrame.from_records( results_list, columns=["time", "device", "num", "savedAt", "scada", "tag"])[["time", "num", "tag"]]
    df = df.pivot(index='time', columns='tag', values='num')
    
    return df

def insert_influx_data(pointId, value, ts, rp='point_transformation'):
    
    unixtime = convertTimeToMs(ts)
    points = [
        {  
            "measurement": "point_value",
            "time": ts,
            "tags": {
                "pointId":pointId
            },
            "fields": {  
                "num": float(value),
                "savedAt": unixtime
            }
        }
    ]
    InfluxDB.client.write_points(points , retention_policy=rp , batch_size= 5000)
    pass