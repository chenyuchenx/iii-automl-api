from pymongo import MongoClient, UpdateOne
from mongo_proxy import MongoProxy
from config import configs as p
from datetime import datetime
import minio, influxdb, app.logs as log

class Minio(object):
    
    init_flag = False
    
    def __init__(self):
        if Minio.init_flag:
            return
        try:
            self.client = minio.Minio( p.MINIO_HOST, p.MINIO_USER, p.MINIO_PASSWORD, secure=True )
            Minio.init_flag = True
            #if self.client.bucket_exists(p.BUCKET_NAME) == False:
            #    self.client.make_bucket(p.BUCKET_NAME)
            log.sys_log.info(f"[DB] Connect minio success: {p.MINIO_HOST}.")
        except Exception as e:
            log.sys_log.error("[DB] Connect minio failed: {}".format(e))

class InfluxDB():
    
    _instance = None
    init_flag = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if InfluxDB.init_flag:
            return
        try:
            url = p.INFLUX_URL.split(':')
            self.client = influxdb.InfluxDBClient(url[0], url[1], p.INFLUX_USERNAME, p.INFLUX_PASSWORD, p.INFLUX_DATABASE)
            connectCheck = self.client.get_list_database()[0].get('name')
            log.sys_log.info(f"[DB] Connect influx: {datetime.now()} - {connectCheck} - connect success .")
            InfluxDB.init_flag = True
        except Exception as e:
            log.sys_log.error(f"[DB] Connect influx: {datetime.now()} - {e} - connect error .")

    def showMeasurements(self):
        return self.client.query('show measurements')
    
    def selectSql(self, execute):
        try:
            results = self.client.query(execute)
        except Exception as e:
            results = []
            log.sys_log.error(f"[DB] execute influx: {datetime.now()} - {e} - connect error .")
        finally:
            return results
    
    def write_points(self, points):
        try:
            results = self.client.write_points(points , retention_policy='point_prediction', batch_size= 5000, protocol = 'json')
            log.sys_log.info(f"[DB] write points: {results}")
        except Exception as e:
            results = None
            log.sys_log.error(f"[DB] execute influx: {datetime.now()} - {e} - connect error .")
        finally:
            return results

class MongoDB(object):
    
    instance = None
    init_flag = False

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        if MongoDB.init_flag:
            return
        
        mongoClient = MongoProxy(MongoClient(p.MONGODB_URL,
                                 username = p.MONGODB_USERNAME,
                                 password = p.MONGODB_PASSWORD,
                                 authSource = p.MONGODB_AUTH_SOURCE,
                                 authMechanism = p.MONGODB_AUTHMECHANISM))
                                 
        self.DATABASE = mongoClient[p.MONGODB_DATABASE]
        log.sys_log.info(f"[DB] Connect mongo success: {p.MONGODB_DATABASE}.")
        MongoDB.init_flag = True
    
    def getOne(self, database, dictRequest):
        mCollection = self.DATABASE[database]
        mDocument = mCollection.find_one(dictRequest)
        return mDocument

    def getMany(self, database, pipeline):
        mCollection = self.DATABASE[database]
        mDocument = mCollection.aggregate(pipeline)
        return list(mDocument)
    
    def insertOne(self, database, document):
        mCollection = self.DATABASE[database]
        x = mCollection.insert_one(document)
        return (x.inserted_id)
    
    def insertMany(self, database, document):
        mCollection = self.DATABASE[database]
        mCollection.insertMany(document)
    
    def updateOne(self, database, myquery, newvalues):
        mCollection = self.DATABASE[database]
        mCollection.update_one(myquery, newvalues)
    
    def updateMany(self, database, myquery, newvalues):
        mCollection = self.DATABASE[database]
        mCollection.update_many(myquery, newvalues)

    def upsertOne(self, database, myquery, newvalues):
        mCollection = self.DATABASE[database]
        mCollection.update_one(myquery, newvalues, upsert=True)
    
    def upsertMany(self, database, operations):
        mCollection = self.DATABASE[database]
        mCollection.bulk_write(operations)
    
    def deleteOne(self, database, document):
        mCollection = self.DATABASE[database]
        mCollection.delete_one(document)
    
    def deleteMany(self, database, document):
        mCollection = self.DATABASE[database]
        mDocument = mCollection.delete_many(document)
        return mDocument
    
    def findOneAndDelete(self, database, dictRequest):
        mCollection = self.DATABASE[database]
        mDocument = mCollection.find_one_and_delete(dictRequest)
        return mDocument
    
    def deleteDatabase(self, database):
        mCollection = self.DATABASE[database]
        mCollection.delete_many({})
    