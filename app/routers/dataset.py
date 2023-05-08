from fastapi import APIRouter, Request, HTTPException, status, Query, Form, UploadFile
from bson.objectid import ObjectId
from config import configs as p
from datetime import datetime
from app.routers import schemas as sc
from app.src import datafunc
import app.database as db, json, app.logs as log

router    = APIRouter()
MongoDB   = db.MongoDB()

@router.get("/source", status_code=status.HTTP_200_OK)
def get_source(*, type: str = Query(..., enum=["csv", "image folder"]), source: str = Query(None, enum=["MinIO", "DataFabric"]), request: Request):

    if source == "MinIO" and type == "csv":
        res = datafunc.getMinIOInfo()
    elif source == "MinIO" and type == "image folder":
        res = []
    elif source == "DataFabric" :
        res = datafunc.getDataFabricInfo()
    elif type == "csv":
        res = ["MinIO", "DataFabric"]
    else:
        res = ["MinIO"]

    return {"data": res, "total":len(res)}

@router.get("/source/detail", status_code=status.HTTP_200_OK)
async def get_source_detail(*, type: str = Query(..., enum=["csv"]), source: str = Query(None, enum=["MinIO", "DataFabric"]), id: str = Query(None),request: Request):

    if source == "MinIO" and type == "csv":
        res = datafunc.getMinIODetail(id)
    elif source == "MinIO" and type == "image folder":
        res = []
    elif source == "DataFabric" :
        res = datafunc.getDataFabricDetail(id)
    else:
        res = []

    return {"data": res, "total":len(res)}

@router.post('/minio/upload', status_code=status.HTTP_201_CREATED)
async def upload_minio_file( request: Request, file: UploadFile , bucketName: str = Form(...)):

    item = await request.form()
    item = dict(item)

    file_name = file.filename.rsplit('.', 1)[0]

    res = datafunc.uploadMinIOFile(file, bucketName, file_name)

    return {'data': {file_name: "success"}}

@router.get("/info", status_code=status.HTTP_200_OK)
async def get_data_info():
    pipeline = [
        {"$addFields": {
            "createdAt":{"$dateToString":{"format": "%Y-%m-%dT%H:%M:%SZ","date":"$createdAt"}},
            "updatedAt"  : { "$dateToString": { "format": "%Y-%m-%dT%H:%M:%SZ", "date": "$updatedAt" } },}
            }, 
        {"$sort" :{"createdAt" : 1}}
    ]
    
    dict_list = MongoDB.getMany(p.mongo_data_info, pipeline)
    for c in dict_list: 
        c['id'] = str(c['_id'])
        del c['_id']

    return {"data": dict_list, "total": len(dict_list)}


@router.post("/info", status_code=status.HTTP_201_CREATED)
def create_data_task(*, item:sc.DataItem, request: Request):

    item = item.__dict__
    
    if not 'name' in item:
        raise HTTPException(status_code=400, detail="name is missing.")
    if not 'source' in item:
        raise HTTPException(status_code=400, detail="source is missing.")
    if not 'type' in item:
        raise HTTPException(status_code=400, detail="type is missing.")
    if not 'storage' in item:
        raise HTTPException(status_code=400, detail="storage is missing.")

    if MongoDB.getMany(p.mongo_data_info, [{"$match":{"name":item.get('name')}}]):
        raise HTTPException(status_code=409, detail="This name already exists.")
    
    if item.get('source') not in {'MinIO', 'DataFabric'}:
        raise HTTPException(status_code=400, detail=f"source only can choose [ MinIO / DataFabric ].")

    item['createdAt'] = datetime.utcnow()
    item['updatedAt'] = datetime.utcnow()
    id = MongoDB.insertOne(p.mongo_data_info, item)

    return {'data': {str(id) : item.get('name')}}

@router.put("/info", status_code=status.HTTP_200_OK)
def update_data_task(*, id: str = Query(...), item:sc.DataItem, request: Request):

    item = item.__dict__

    check = MongoDB.getMany(p.mongo_data_info, [{"$match":{"_id": ObjectId(id)}}])
    if len(check) == 0 :
        raise HTTPException(status_code=404, detail=f"This id : {id} not found.")
    
    if item.get('source') is not None and item.get('source') not in {'MinIO', 'DataFabric'}:
        raise HTTPException(status_code=400, detail=f"source only can choose [ MinIO / DataFabric ].")
    
    item['updatedAt'] = datetime.utcnow()

    MongoDB.upsertOne(p.mongo_data_info, {'_id':ObjectId(id)}, {"$set": item})

    return {'data': {id: "success"}}

@router.delete("/info", status_code=status.HTTP_200_OK )
def delete_data_task(*, id: str = Query(...), request: Request):
    try:
        check = MongoDB.getOne(p.mongo_data_info, {"_id":ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"id : {id} ,error : {e}.")
    if check is None:
        raise HTTPException(status_code=404, detail=f"This id: {id} not found.")
    
    dictDoc = MongoDB.findOneAndDelete(p.mongo_data_info, {'_id':ObjectId(id)})

    return {'data': {id: "delete"}}

@router.get("/features", status_code=status.HTTP_200_OK)
async def get_data_features(*, id: str = Query(...)):

    data = MongoDB.getOne(p.mongo_data_info, {"_id":ObjectId(id)})

    if data.get('source') == "MinIO" and data.get('type') == "csv":
        res = datafunc.getMinioFeature(data)
    elif data.get('source') == "MinIO" and data.get('type') == "image folder":
        res = []
    elif data.get('source') == "DataFabric" :
        res = []
    else:
        res = []

    return {"data": res, "total":len(res)}

@router.get("/features/matrix", status_code=status.HTTP_200_OK)
async def get_data_features_corr_matrix(*, id: str = Query(...), target: str = Query(...)):

    data = MongoDB.getOne(p.mongo_data_info, {"_id":ObjectId(id)})

    if data.get('source') == "MinIO" and data.get('type') == "csv":
        res = datafunc.getMinioFeatureCorrMatrix(data, target)
    elif data.get('source') == "MinIO" and data.get('type') == "image folder":
        res = []
    elif data.get('source') == "DataFabric" :
        res = []
    else:
        res = []

    return {"data": res, "total":len(res)}
