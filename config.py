from pydantic import BaseSettings, Field
from functools import lru_cache
from typing import Optional
import logging, os, json

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """System configurations."""

    SKIP_TLS: Optional[bool]               = Field(False, env="SKIP_TLS")
    TIME_OUT_LIMIT: Optional[int]          = Field(10, env="TIME_OUT_LIMIT")
    IS_SSL_ENABLE: Optional[bool]          = Field(False, env="IS_SSL_ENABLE")
    IS_SSL_CERTIFICATE_FILE: Optional[str] = Field(None, env="IS_SSL_CERTIFICATE_FILE")
    IS_SSL_PRIVATE_KEY_FILE: Optional[str] = Field(None, env="IS_SSL_PRIVATE_KEY_FILE")

    IAPP_NAME: Optional[str]         = Field("iii-automl-api", env="IAPP_NAME")
    IAPP_VERSION: Optional[str]      = Field("0.0.8", env="IAPP_VERSION")
    IAPP_NAME_CAPITAL: Optional[str] = Field(None, env="IAPP_NAME_CAPITAL")
    IAPP_NAME_LOWER: Optional[str]   = Field(None, env="IAPP_NAME_LOWER")
    IAPP_UI_URL: Optional[str]       = Field(None, env="IAPP_UI_URL")
    IAPP_API_URL: Optional[str]      = Field(None, env="IAPP_API_URL")

    IS_UPPER: Optional[bool]          = Field(False, env="IS_UPPER")
    IS_LICENSE: Optional[bool]        = Field(True, env="IS_LICENSE")   #False 走測試
    SHOW_LICENSE: Optional[bool]      = Field(True, env="SHOW_LICENSE")

    ENVIRONMENT: Optional[str]      = Field("production", env="ENVIRONMENT")
    CLUSTER: Optional[str]          = Field(None, env="cluster")
    NAMESPACE: Optional[str]        = Field(None, env="namespace")
    EXTERNAL: Optional[str]         = Field(None, env="external")
    WORKSPACE: Optional[str]        = Field(None, env="workspace")
    ENSAAS_SERVICES: Optional[dict] = Field(None, env="ENSAAS_SERVICES")

    MONGODB_URL: Optional[str]           = Field(None, env="MONGODB_URL")
    MONGODB_DATABASE: Optional[str]      = Field(None, env="MONGODB_DATABASE")
    MONGODB_USERNAME: Optional[str]      = Field(None, env="MONGODB_USERNAME")
    MONGODB_PASSWORD: Optional[str]      = Field(None, env="MONGODB_PASSWORD")
    MONGODB_PASSWORD_FILE: Optional[str] = Field(None, env="MONGODB_PASSWORD_FILE")
    MONGODB_AUTH_SOURCE: Optional[str]   = Field(None, env="MONGODB_AUTH_SOURCE")
    MONGODB_AUTHMECHANISM: Optional[str] = Field("SCRAM-SHA-1", env="MONGODB_AUTHMECHANISM")

    POSTGRES_URL: Optional[str]           = Field(None, env="POSTGRES_URL")
    POSTGRES_DATABASE: Optional[str]      = Field(None, env="POSTGRES_DATABASE")
    POSTGRES_USERNAME: Optional[str]      = Field(None, env="POSTGRES_USERNAME")
    POSTGRES_PASSWORD: Optional[str]      = Field(None, env="POSTGRES_PASSWORD")
    POSTGRES_PASSWORD_FILE: Optional[str] = Field(None, env="POSTGRES_PASSWORD_FILE")

    REDIS_URL: Optional[str]            = Field(None, env="REDIS_URL")
    REDIS_DATABASE: Optional[str]       = Field("ifp_redis", env="REDIS_DATABASE")
    REDIS_PASSWORD: Optional[str]       = Field(None, env="REDIS_PASSWORD")
    REDIS_PASSWORD_FILE: Optional[str]  = Field(None, env="REDIS_PASSWORD_FILE")

    INFLUX_URL: Optional[str]           = Field(None, env="INFLUX_URL")
    INFLUX_DATABASE: Optional[str]      = Field(None, env="INFLUX_DATABASE")
    INFLUX_USERNAME: Optional[str]      = Field(None, env="INFLUX_USERNAME")
    INFLUX_PASSWORD: Optional[str]      = Field(None, env="INFLUX_PASSWORD")
    INFLUX_PASSWORD_FILE: Optional[str] = Field(None, env="INFLUX_PASSWORD_FILE")

    MINIO_HOST: Optional[str]     = Field(None, env="MINIO_HOST")
    MINIO_USER: Optional[str]     = Field(None, env="MINIO_USER")
    MINIO_PASSWORD: Optional[str] = Field(None, env="MINIO_PASSWORD")
    BUCKET_NAME: Optional[str]    = Field("Model Storage", env="BUCKET_NAME")

    IFPS_DATAFABRIC_API_URL: Optional[str]  = Field(None, env="IFPS_DATAFABRIC_API_URL")
    
    class Config:
        env_file = ".env"

class Config(Settings):

    os.environ['CUDA_VISIBLE_DEVICES'] = "0" # 關閉 tensorflow-gpu 不匹配 warning
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = "2" # 關閉 tensorflow warning =2 額外隱藏WARNING logs
    os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = "python"
    
    if Settings().ENSAAS_SERVICES is not None:
        ENSAAS_SERVICES = Settings().ENSAAS_SERVICES
        if 'mongodb' in ENSAAS_SERVICES:
            MONGODB_URL = ENSAAS_SERVICES.get('mongodb')[0].get('credentials').get('externalHosts')
            MONGODB_DATABASE = ENSAAS_SERVICES.get('mongodb')[0].get('credentials').get('database')
            MONGODB_USERNAME = ENSAAS_SERVICES.get('mongodb')[0].get('credentials').get('username')
            MONGODB_PASSWORD = ENSAAS_SERVICES.get('mongodb')[0].get('credentials').get('password')
            MONGODB_AUTH_SOURCE = MONGODB_DATABASE
        if 'postgresql' in ENSAAS_SERVICES:
            POSTGRES_URL = ENSAAS_SERVICES.get('postgresql')[0].get('credentials').get('externalHosts')
            POSTGRES_DATABASE = ENSAAS_SERVICES.get('postgresql')[0].get('credentials').get('database')
            POSTGRES_USERNAME = ENSAAS_SERVICES.get('postgresql')[0].get('credentials').get('username')
            POSTGRES_PASSWORD = ENSAAS_SERVICES.get('postgresql')[0].get('credentials').get('password')
        if 'redis' in ENSAAS_SERVICES:
            REDIS_HOST = ENSAAS_SERVICES.get('redis')[0].get('credentials').get('host')
            REDIS_PORT = ENSAAS_SERVICES.get('redis')[0].get('credentials').get('port')
            REDIS_URL = f"{REDIS_HOST}:{REDIS_PORT}"
            REDIS_PASSWORD = ENSAAS_SERVICES.get('redis')[0].get('credentials').get('password')
        if 'influxdb' in ENSAAS_SERVICES:
            INFLUX_URL = ENSAAS_SERVICES.get('influxdb')[0].get('credentials').get('externalHosts')
            INFLUX_DATABASE = ENSAAS_SERVICES.get('influxdb')[0].get('credentials').get('database')
            INFLUX_USERNAME = ENSAAS_SERVICES.get('influxdb')[0].get('credentials').get('username')
            INFLUX_PASSWORD = ENSAAS_SERVICES.get('influxdb')[0].get('credentials').get('password')
    
    if Settings().MONGODB_PASSWORD == None and Settings().MONGODB_PASSWORD_FILE is not None:
        existence = os.path.exists(Settings().MONGODB_PASSWORD_FILE)
        if existence:
            MONGODB_PASSWORD = open(Settings().MONGODB_PASSWORD_FILE).read().rstrip('\n')
    if Settings().POSTGRES_PASSWORD == None and Settings().POSTGRES_PASSWORD_FILE is not None:
        existence = os.path.exists(Settings().POSTGRES_PASSWORD_FILE)
        if existence:
            POSTGRES_PASSWORD = open(Settings().POSTGRES_PASSWORD_FILE).read().rstrip('\n')
    if Settings().REDIS_PASSWORD == None and Settings().REDIS_PASSWORD_FILE is not None:
        existence = os.path.exists(Settings().REDIS_PASSWORD_FILE)
        if existence:
            REDIS_PASSWORD = open(Settings().REDIS_PASSWORD_FILE).read().rstrip('\n')
    if Settings().INFLUX_PASSWORD == None and Settings().INFLUX_PASSWORD_FILE is not None:
        existence = os.path.exists(Settings().INFLUX_PASSWORD_FILE)
        if existence:
            INFLUX_PASSWORD = open(Settings().INFLUX_PASSWORD_FILE).read().rstrip('\n')
    
    """ Mapping Url """
    if Settings().IAPP_API_URL is None and Settings().EXTERNAL is not None:
        IAPP_UI_URL              = "https://ifps-inference-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL
        IAPP_API_URL             = "https://ifps-inference-api-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL
    else:
        IAPP_UI_URL              = "https://ifps-inference:5000"
        IAPP_API_URL             = "https://ifps-inference-api:5000"
    if Settings().IFPS_DATAFABRIC_API_URL is None and Settings().EXTERNAL is not None:
        IFPS_DATAFABRIC_API_URL = "https://ifps-datafabric-api-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL

    # global
    mongo_data_info           = "iii.data.info"
    mongo_task_info           = "iii.task.info"
    mongo_model_repo          = "iii.model.repo"
    mongo_model_info          = "iii.model.info"
    
    """ Logging all env is upper not Include ENSAAS_SERVICES """
    logging.basicConfig(level=logging.INFO)
    for key in range(len(dir())):
        if dir()[key].isupper() is True and dir()[key] != "ENSAAS_SERVICES" and locals()[dir()[key]] is not None:
            logging.info(f"[ENV]  {dir()[key]} ok ... : {locals()[dir()[key]]}")

@lru_cache()
def get_configs():
    return Config()

configs = get_configs()

#print(configs)