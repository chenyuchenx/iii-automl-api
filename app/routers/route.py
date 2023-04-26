from fastapi import APIRouter, Request, HTTPException, status, Query
from pymongo import UpdateOne
from config import configs as p
from datetime import datetime
from app.routers import schemas as sc
import app.database as db, requests, json, numpy, app.logs as log

router = APIRouter()
MongoDB   = db.MongoDB()

@router.get("/models/infer", status_code=status.HTTP_200_OK)
@router.post('/models/infer', status_code=status.HTTP_201_CREATED)
def get_model_infer(*, id: str = Query(...), machineId: str = Query(None), kind: str = Query(None),inputs: sc.InferItemListResponse, request: Request):

    
    pass

    return {"data": [], "total":0}