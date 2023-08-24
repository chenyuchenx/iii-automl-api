from fastapi import HTTPException
from pymongo import UpdateOne
from config import configs as p
import app.database as db, app.src as utils, app.logs as log, pandas as pd, io, numpy as np, zipfile, tempfile, os, shutil

MongoDB   = db.MongoDB()
Minio     = db.Minio()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1] in ['csv']

def uploadMinIOFile(file, bucket, name):

    if Minio.client.bucket_exists(bucket) == False:
        Minio.client.make_bucket(bucket)

    if file and allowed_file(file.filename):
        try:
            content = file.file.read()
            Minio.client.put_object( bucket_name=bucket, object_name=f"{name}.csv", data=io.BytesIO(content), length=len(content), content_type='text/csv')
        except Exception as exc:
            log.sys_log.error(f"[MinIO] upload Error occurred: {exc}")
            raise HTTPException(status_code=400, detail=f"[MinIO] upload Error occurred: {exc}")
    else:
        raise HTTPException(status_code=400, detail="Format error, please upload csv format file.")

def getMinIOInfo():

    buckets = Minio.client.list_buckets()
    bucket_dict_list = [{'id': bucket.name, 'name': bucket.name,'parentId':''} for bucket in buckets]

    return bucket_dict_list

def getMinIODetail(id):
    object_list = []

    try:
        objects = Minio.client.list_objects(id, recursive=True)
        for obj in objects:
            if obj.object_name.endswith('.csv'):
                object_path = obj.object_name
                if object_path.startswith(id + '/'): 
                    object_path = object_path[len(id) + 1:]
                if '/' not in object_path:
                    object_dict = {'name': object_path, 'bucketName': id, 'path': '', 'updatedAt': obj.last_modified, 'size': obj.size}
                else:
                    path_parts = object_path.split('/')
                    path = ''
                    for part in path_parts[:-1]:
                        path += part + '/'
                    object_dict = {'name': path_parts[-1], 'bucketName': id, 'path': path, 'updatedAt': obj.last_modified, 'size': obj.size}
                object_list.append(object_dict)
    except Exception as e:
        log.sys_log.error(f"[Minio] get minio obj detail error:{e}")

    return object_list

def getMinIOImage(id):
    object_list = []

    try:
        objects = Minio.client.list_objects(id, recursive=True)
        for obj in objects:
            if obj.object_name.endswith('.zip'):
                object_path = obj.object_name
                if object_path.startswith(id + '/'): 
                    object_path = object_path[len(id) + 1:]
                if '/' not in object_path:
                    object_dict = {'name': object_path, 'bucketName': id, 'path': '', 'updatedAt': obj.last_modified, 'size': obj.size}
                else:
                    path_parts = object_path.split('/')
                    path = ''
                    for part in path_parts[:-1]:
                        path += part + '/'
                    object_dict = {'name': path_parts[-1], 'bucketName': id, 'path': path, 'updatedAt': obj.last_modified, 'size': obj.size}
                object_list.append(object_dict)
    except Exception as e:
        log.sys_log.error(f"[Minio] get minio obj detail error:{e}")

    return object_list

def getMinioImageFeature(data):
    storage = data.get('storage')
    object_name = storage.get('path')+storage.get('name')

    temp_dir = tempfile.mkdtemp()
    folder_image_count = {} 
    
    try:
        local_zip_file = os.path.join(temp_dir, 'temp.zip')
        Minio.client.fget_object(storage.get('bucketName'), object_name, local_zip_file)

        with zipfile.ZipFile(local_zip_file, 'r') as zip_file:
            for file_name in zip_file.namelist():
                if file_name.endswith(('.jpg', '.png')):
                    folder_name = os.path.basename(os.path.dirname(file_name))
                    folder_image_count[folder_name] = folder_image_count.get(folder_name, 0) + 1
    except Exception as e:
        print(f"[Error] getMinioImageFeature : {e}")
    finally:
        shutil.rmtree(temp_dir)
        image_list = []

        for key, value in folder_image_count.items():
            image_dict = {"name": key, "type": "image", "Count": value, "nullCount": 0}
            image_list.append(image_dict)

        return(image_list)

def getMinioFeature(data):

    storage = data.get('storage')
    object_name = storage.get('path')+storage.get('name')
    object = Minio.client.get_object(storage.get('bucketName'), object_name).read()
    df = pd.read_csv(io.BytesIO(object))
    cols = [{"name": c, "type": str(t)} for c, t in df.dtypes.items()]
    columns = [{"name": column, "type": str(df[column].dtype), "Count": int(df[column].count()), "nullCount": int(df[column].isnull().sum())} for column in df.columns]

    return columns

def getMinioFeatureCorrMatrix(data, target):
    
    storage = data.get('storage')
    object_name = storage.get('path')+storage.get('name')
    object = Minio.client.get_object(storage.get('bucketName'), object_name).read()
    df = pd.read_csv(io.BytesIO(object))
    columns = [{"name": column, "type": str(df[column].dtype), "nullCount": int(df[column].isnull().sum())} for column in df.columns]

    df = df.apply(pd.to_numeric, errors='coerce')
    corr_matrix = df.corr().abs()

    for column in columns:
        if column["name"] == target:
            if column["type"] == 'object':
                column["problemType"] = "classification"
            else:
                min_value = df[target].min()
                max_value = df[target].max()
                if max_value - min_value > 10:
                    column["problemType"] = "linear"
                else:
                    column["problemType"] = "classification"
            continue
        correlation_score = corr_matrix.loc[target, column["name"]]
        column["corrScore"] = np.nan_to_num(correlation_score)

    return columns

def getDataFabricInfo():

    object_list = []
    
    res, r_status = utils.requestsApi("GET", f"{p.III_DATAFABRIC_API_URL}/dataset")# headers=headers
    if r_status == 200 : 
        for item in res:
            object_list.append({"id":item.get('disTableName') ,"name":item.get('datasetName'),"parentId":item.get('ParentID')})

    return [{"id":"DEZYEoqbvaZW", "name":"Datafabric Dataset Zone", "parentId":None}]

def getDataFabricDetail(id):
    
    object_list = []
    
    res, r_status = utils.requestsApi("GET", f"{p.III_DATAFABRIC_API_URL}/dataset")# headers=headers
    if r_status == 200 : 
        for item in res:
            object_dict = {'name': item.get('datasetName'), 'bucketName': id, 'path': item.get('disTableName'), 'updatedAt': item.get('updatedAt'), 'size': item.get('datasetSize')}
            object_list.append(object_dict)
            
    return object_list

def getDataFabricFeature(data):
    
    storage = data.get('storage')
    object_name = storage.get('path')
    data, r_status = utils.requestsApi("GET", f"{p.III_DATAFABRIC_API_URL}/data/query/api?name={object_name}")
    columns = [column['name'] for column in data['columns']]
    rows = [[item['v'] for item in row['row']] for row in data['rows']]
    df = pd.DataFrame(rows, columns=columns)

    cols = [{"name": c, "type": str(t)} for c, t in df.dtypes.items()]
    columns = [{"name": column, "type": str(df[column].dtype), "nullCount": int(df[column].isnull().sum())} for column in df.columns]

    return columns

def getDataFabricFeatureCorrMatrix(data, target):
    
    storage = data.get('storage')
    object_name = storage.get('path')
    data, r_status = utils.requestsApi("GET", f"{p.III_DATAFABRIC_API_URL}/data/query/api?name={object_name}")
    columns = [column['name'] for column in data['columns']]
    rows = [[item['v'] for item in row['row']] for row in data['rows']]
    df = pd.DataFrame(rows, columns=columns)

    columns = [{"name": column, "type": str(df[column].dtype), "nullCount": int(df[column].isnull().sum())} for column in df.columns]

    df = df.apply(pd.to_numeric, errors='coerce')
    corr_matrix = df.corr().abs()

    for column in columns:
        if column["name"] == target:
            if column["type"] == 'object':
                column["problemType"] = "classification"
            else:
                min_value = df[target].min()
                max_value = df[target].max()
                if max_value - min_value > 10:
                    column["problemType"] = "linear"
                else:
                    column["problemType"] = "classification"
            continue
        correlation_score = corr_matrix.loc[target, column["name"]]
        column["corrScore"] = np.nan_to_num(correlation_score)

    return columns