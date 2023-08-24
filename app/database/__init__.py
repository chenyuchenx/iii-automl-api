from pymongo import MongoClient
from mongo_proxy import MongoProxy
from config import configs as p
import minio, app.logs as log

class Minio(object):
    
    init_flag = False
    
    def __init__(self):
        if Minio.init_flag:
            return
        try:
            self.client = minio.Minio(p.MINIO_HOST, p.MINIO_USER, p.MINIO_PASSWORD, secure=True)
            self.initialize_minio()
        except Exception as e:
            log.sys_log.error(f"[MDB] Connect minio error: {str(e)}.")

    def initialize_minio(self):
        Minio.init_flag = True
        if not self.client.bucket_exists(p.BUCKET_NAME):
            self.client.make_bucket(p.BUCKET_NAME)
            log.sys_log.info(f"[MDB] Connect minio success: {p.MINIO_HOST}. Created bucket: {p.BUCKET_NAME}.")

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
        
        try:
            mongoClient = MongoProxy(MongoClient(p.MONGODB_URL,
                                     username = p.MONGODB_USERNAME,
                                     password = p.MONGODB_PASSWORD,
                                     authSource = p.MONGODB_AUTH_SOURCE,
                                     authMechanism = p.MONGODB_AUTHMECHANISM))

            self.DATABASE = mongoClient[p.MONGODB_DATABASE]
            log.sys_log.info(f"[MDB] Connect mongo success: {p.MONGODB_DATABASE}.")
            MongoDB.init_flag = True
        except Exception as e:
            log.sys_log.error(f"[MDB] Connect mongo error: {str(e)}.")
    
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
    