from fastapi import APIRouter, Request, HTTPException, status, Query, Form, UploadFile
from bson.objectid import ObjectId
from config import configs as p
from datetime import datetime
from app.routers import schemas as sc
from app.src.datafunc import allowed_file
import app.database as db, pandas as pd, numpy as np, app.logs as log, requests, json

router = APIRouter()
MongoDB   = db.MongoDB()

@router.get("/type", status_code=status.HTTP_200_OK)
async def get_task_type():
    
    types = ["Tabuler Prediction", "Image Classification", "Object Detection"]

    return {"data": types, "total":len(types)}

@router.get("/algo", status_code=status.HTTP_200_OK)
async def get_task_algo():
    
    algos = ["AutoKeras", "AutoScikit", "AutoPytorch"]

    return {"data": algos, "total":len(algos)}

@router.get("/mode/default", status_code=status.HTTP_200_OK)
async def get_task_mode_default():
    
    modes = [
        {
            "testSize" : 0.2,
            "timeLimit" : None,
            "trials" : 10,
            "epochs": 20,
            "algo" : [ 
                "AutoKeras", 
                "AutoScikit"
            ],
            "callBack" : False
        }
    ]

    return {"data": modes, "total":len(modes)}

@router.get("/info", status_code=status.HTTP_200_OK)
async def get_batch_task_info():
    pipeline = [
        {"$addFields": {
            "trainStartAt":{"$dateToString":{"format": "%Y-%m-%dT%H:%M:%SZ","date":"$trainStartAt"}},
            "trainEndAt":{"$dateToString":{"format": "%Y-%m-%dT%H:%M:%SZ","date":"$trainEndAt"}},
            "createdAt":{"$dateToString":{"format": "%Y-%m-%dT%H:%M:%SZ","date":"$createdAt"}},
            "updatedAt"  : { "$dateToString": { "format": "%Y-%m-%dT%H:%M:%SZ", "date": "$updatedAt" } },}
            }, 
        {"$sort" :{"createdAt" : 1}}
    ]
    
    tasks = MongoDB.getMany(p.mongo_task_info, pipeline)
    for task in tasks: 
        task['id'] = str(task.pop('_id'))
        task['dataset']['id'] = str(task['dataset']['id'])
        task['repo']['id'] = str(task['repo'].get('id'))

    return {"data": tasks, "total":len(tasks)}

@router.post("/info", status_code=status.HTTP_201_CREATED)
def create_batch_task(*, item:sc.TaskItem, request: Request):

    item = item.__dict__

    if not 'name' in item:
        raise HTTPException(status_code=400, detail="name is missing.")
    if not 'type' in item:
        raise HTTPException(status_code=400, detail="source is missing.")
    if not 'dataset' in item:
        raise HTTPException(status_code=400, detail="type is missing.")
    if not 'mode' in item:
        raise HTTPException(status_code=400, detail="storage is missing.")

    if MongoDB.getMany(p.mongo_task_info, [{"$match":{"name":item.get('name')}}]):
        raise HTTPException(status_code=409, detail="This name already exists.")
    
    if item.get('type') not in {'Tabuler Prediction', 'Image Classification', 'Object Detection'}:
        raise HTTPException(status_code=400, detail=f"source only can choose [ Tabuler Prediction / Image Classification / Object Detection ].")

    item['state'] = "Created"
    item['status'] = 0
    item['trainStartAt'] = None
    item['trainEndAt'] = None
    item['createdAt'] = datetime.utcnow()
    item['updatedAt'] = datetime.utcnow()
    item['dataset']['id'] = ObjectId(item['dataset']['id'] )
    item['repo']['id'] = ObjectId(item['repo']['id'] )

    id = MongoDB.insertOne(p.mongo_task_info, item)

    return {'data': {str(id) : item.get('name')}}

@router.put("/info", status_code=status.HTTP_200_OK)
def update_batch_task(*, id: str = Query(...), item:sc.TaskItem, request: Request):

    item = item.__dict__

    check = MongoDB.getMany(p.mongo_task_info, [{"$match":{"_id": ObjectId(id)}}])
    if len(check) == 0 :
        raise HTTPException(status_code=404, detail=f"This id : {id} not found.")
    
    if item.get('type') not in {'Tabuler Prediction', 'Image Classification', 'Object Detection'}:
        raise HTTPException(status_code=400, detail=f"source only can choose [ Tabuler Prediction / Image Classification / Object Detection ].")
    
    item['updatedAt'] = datetime.utcnow()

    MongoDB.upsertOne(p.mongo_data_info, {'_id':ObjectId(id)}, {"$set": item})

    return {'data': {id: "success"}}

@router.post("/info/train", status_code=status.HTTP_200_OK)
async def post_train(*, id: str = Form(...), state: str = Form(..., enum=["Created", "Stopped", "Cancel"]), request: Request):

    check = MongoDB.getMany(p.mongo_task_info, [{"$match":{"_id": ObjectId(id)}}])
    if len(check) == 0 :
        raise HTTPException(status_code=404, detail=f"This id : {id} not found.")
    
    if state not in {'Created', 'Stopped', 'Cancel'}:
        raise HTTPException(status_code=400, detail=f"state only can choose [ Created / Stopped / Cancel ].")
    
    MongoDB.upsertOne(p.mongo_task_info, {'_id':ObjectId(id)}, {"$set": { 'updatedAt': datetime.utcnow(), "isActive" : False, "state" : state, "status" : 0 }})

    if state == "Created":
        r = requests.request("POST", f"{p.IFPS_AUTOML_ENGINE_URL}/api/task", data={'id': id, 'state': state}, timeout=p.TIME_OUT_LIMIT, headers={}, verify=p.SKIP_TLS)
        if r.status_code == 200:
            return {'data': {id: "success"}}
        else:
            raise HTTPException(status_code=r.status_code, detail=f"{r.text}")

    return {'data': {id: "success"}}

@router.delete("/info", status_code=status.HTTP_200_OK )
def delete_batch_task_task(*, id: str = Query(...), request: Request):
    try:
        check = MongoDB.getOne(p.mongo_task_info, {"_id":ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"id : {id} ,error : {e}.")
    if check is None:
        raise HTTPException(status_code=404, detail=f"This id: {id} not found.")
    
    task = MongoDB.findOneAndDelete(p.mongo_task_info, {'_id':ObjectId(id)})

    return {'data': {id: "delete"}}

@router.get("/info/eval", status_code=status.HTTP_200_OK)
async def get_batch_task_info_eval(*, id: str = Query(...)):
    
    try:
        check = MongoDB.getOne(p.mongo_task_info, {"_id":ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"id : {id} ,error : {e}.")
    if check is None:
        raise HTTPException(status_code=404, detail=f"id: {id} not found.")
    
    time_diff = check.get("trainEndAt") - check.get("trainStartAt")

    tasks = [{
        "name":check.get("name"),
        "createdAt":check.get("createdAt"),
        "trainingDuration":time_diff,
        "accuracy":check.get("accuracy"),
        "target":check.get("dataset").get("target"),
        "feature":check.get("dataset").get("feature"),
        "problem":"Binary",
        "mode":check.get("mode"),
        "trials":[
            {
                "name":"structured_data_block_1/normalize",
                "accuracy":0.6826922
            },
            {
                "name":"structured_data_2/rf",
                "accuracy":0.5936417
            }
        ]
    }]

    return {"data": tasks, "total":len(tasks)}

@router.post('/info/infer', status_code=status.HTTP_201_CREATED)
async def post_batch_task_info_infer(*, id: str = Form(...), request: Request, file: UploadFile):

    if file and allowed_file(file.filename):
        try:
            file_data = await file.read()  # 讀取檔案資料
            files = {'file': (file.filename, file_data)}
            r = requests.request("POST", f"{p.IFPS_AUTOML_ENGINE_URL}/api/task/info/infer", data={'id': id}, files=files, timeout=p.TIME_OUT_LIMIT, headers={}, verify=p.SKIP_TLS)
            r.raise_for_status()  # 若請求失敗會拋出異常
            return r.json()
        except Exception as e:
            log.sys_log.error(f"[Task] inference Error occurred: {e}")
            raise HTTPException(status_code=400, detail=f"[Task] inference Error occurred: {e}")
    else:
        raise HTTPException(status_code=400, detail="Format error, please upload csv format file.")