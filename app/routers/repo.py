from fastapi import APIRouter, Request, HTTPException, status, Query, Form
from bson.objectid import ObjectId
from config import configs as p
from datetime import datetime
from app.routers import schemas as sc
import app.database as db, requests, json, numpy, app.logs as log

router = APIRouter()
MongoDB   = db.MongoDB()

@router.get("/info", status_code=status.HTTP_200_OK)
async def get_repo_info():
    pipeline = [
        {"$lookup":{"from":p.mongo_model_info, "localField":"_id", "foreignField":"repoId", "as":"repolst",}},
        {"$unwind": {"path": "$repolst","preserveNullAndEmptyArrays": True}},
        {
            "$group":
            {
                "_id": "$_id",
                "name" : {"$first" : "$name"},
                "total": {"$sum": {"$cond": [{"$gt": ["$repolst", None]}, 1, 0]}},
                "size": {"$sum": "$repolst.size"},
                "createdAt" : {"$first" : "$createdAt"},
                "updatedAt" : {"$first" : "$updatedAt"}
            }
        },
        {   
            "$addFields": {
                "createdAt":{"$dateToString":{"format": "%Y-%m-%dT%H:%M:%SZ","date":"$createdAt"}},
                "updatedAt"  : { "$dateToString": { "format": "%Y-%m-%dT%H:%M:%SZ", "date": "$updatedAt" } },}
        }, 
        {"$sort" :{"createdAt" : 1}}
    ]
    
    repo_list = MongoDB.getMany(p.mongo_model_repo, pipeline)
    for item in repo_list: 
        item['id'] = str(item.pop('_id'))
        kb_size = item.get('size')/1024
        if kb_size < 1024:
            item['size'] = kb_size
            item['unit'] = 'KB'
        else:
            item['size'] = round(kb_size / 1024, 2)
            item['unit'] = 'MB'

    return {"data": repo_list, "total": len(repo_list)}

@router.post("/info", status_code=status.HTTP_201_CREATED)
async def create_repo_info(*, name: str = Form(...)):

    if MongoDB.getMany(p.mongo_model_repo, [{"$match":{"name":name}}]):
        raise HTTPException(status_code=409, detail="This name already exists.")

    item = {"name":name, "total" : 0, "size" : "0MB", "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()}
    id = MongoDB.insertOne(p.mongo_model_repo, item)

    return {'data': {str(id) : item.get('name')}}

@router.put("/info", status_code=status.HTTP_200_OK)
def update_repo_info(*, id: str = Query(...), name: str = Form(...)):

    check = MongoDB.getMany(p.mongo_model_repo, [{"$match":{"_id": ObjectId(id)}}])
    if len(check) == 0 :
        raise HTTPException(status_code=404, detail=f"This id : {id} not found.")
    
    item = {"name":name, "updatedAt": datetime.utcnow()}
    MongoDB.upsertOne(p.mongo_model_repo, {'_id':ObjectId(id)}, {"$set": item})

    return {'data': {id: "success"}}


@router.delete("/info", status_code=status.HTTP_200_OK )
def delete_repo_task(*, id: str = Query(...), request: Request):
    try:
        check = MongoDB.getOne(p.mongo_model_repo, {"_id":ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"id : {id} ,error : {e}.")
    if check is None:
        raise HTTPException(status_code=404, detail=f"This id: {id} not found.")
    
    task = MongoDB.findOneAndDelete(p.mongo_model_repo, {'_id':ObjectId(id)})

    return {'data': {id: "delete"}}

@router.get("/info/detail", status_code=status.HTTP_200_OK)
def get_repo_model_info(*, id: str = Query(..., description= "[Get] /id to find detail."), request: Request): 

    pipeline = [
        {"$match":{"repoId":ObjectId(id)}},
        { 
            "$group": {
                "_id": "$taskId", 
                "total": { "$sum": 1 },
                "name" : {"$first" : "$name"},
                "data": { 
                    "$push": {
                        "_id": "$_id",
                        "version": "$version",
                        "target": "$target", 
                        "loss": "$loss", 
                        "size": "$size",
                        "dataName": "$dataName",
                        "createdAt": "$createdAt"
                    }
                } 
            } 
        },
        {"$sort" :{"name" : 1}}
    ]

    model_list = MongoDB.getMany(p.mongo_model_info, pipeline)

    for obj in model_list:
        obj['id'] = str(obj.pop('_id'))
        if obj.get('data') is not None:
            for x in obj.get('data'):
                x['id'] = str(x.pop('_id'))

    return {"data": model_list, "total":len(model_list)}

@router.get("/info/detail/version", status_code=status.HTTP_200_OK)
def get_repo_model_info_version(*, version: str = Query(..., description= "[Get] /version to find detail.")): 

    model = MongoDB.getOne(p.mongo_model_detail, {"version": version})
    model = {k: v for k, v in model.items() if k != '_id'}
    model['trend'] = [{k: v.strftime('%Y-%m-%dT%H:%M:%SZ') if k == 'ts' else v for k, v in trend.items()} for trend in model['trend']]

    return {"data": model, "total":len([model])}
