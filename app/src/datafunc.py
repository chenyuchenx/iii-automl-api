from fastapi import HTTPException
from pymongo import UpdateOne
from config import configs as p
import logging, app.database as db, app.src as utils, app.logs as log

MongoDB   = db.MongoDB()
Minio     = db.Minio()

def getMinIOInfo():

    buckets = Minio.client.list_buckets()
    bucket_dict_list = [{'name': bucket.name} for bucket in buckets]

    return bucket_dict_list

def getMinIODetail(name):
    object_list = []

    try:
        objects = Minio.client.list_objects(name, recursive=True)
        for obj in objects:
            if obj.object_name.endswith('.csv'):
                object_path = obj.object_name
                if object_path.startswith(name + '/'): 
                    object_path = object_path[len(name) + 1:]
                if '/' not in object_path:
                    object_dict = {'name': object_path, 'bucketName': name, 'path': '', 'updatedAt': obj.last_modified, 'size': obj.size}
                else:
                    path_parts = object_path.split('/')
                    path = ''
                    for part in path_parts[:-1]:
                        path += part + '/'
                    object_dict = {'name': path_parts[-1], 'bucketName': name, 'path': path, 'updatedAt': obj.last_modified, 'size': obj.size}
                object_list.append(object_dict)
    except Exception as e:
        log.sys_log.error(f"[Minio] get minio obj detail error:{e}")

    return object_list

def getDataFabricInfo():
    
    dictList = []

    return dictList

def getDataFabricDetail(name):
    
    dictList = []

    return dictList