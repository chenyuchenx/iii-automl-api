from fastapi import APIRouter, Request, HTTPException, status, Query, Form
from bson.objectid import ObjectId
from config import configs as p
from datetime import datetime
from app.routers import schemas as sc
import app.database as db, requests, json, numpy, app.logs as log

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
            "trials" : 100,
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