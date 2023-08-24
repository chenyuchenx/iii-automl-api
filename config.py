from pydantic import BaseSettings, Field
from functools import lru_cache
from typing import Optional
import logging, os

logger = logging.getLogger(__name__)

class Settings(BaseSettings):

    IS_TLS_ENABLE: Optional[bool]          = Field(False, env="IS_TLS_ENABLE")
    IS_TLS_TIME_LIMIT: Optional[int]       = Field(10, env="IS_TLS_TIME_LIMIT")
    IS_SSL_ENABLE: Optional[bool]          = Field(False, env="IS_SSL_ENABLE")
    IS_SSL_CERTIFICATE_FILE: Optional[str] = Field(None, env="IS_SSL_CERTIFICATE_FILE")
    IS_SSL_PRIVATE_KEY_FILE: Optional[str] = Field(None, env="IS_SSL_PRIVATE_KEY_FILE")

    IAPP_NAME: Optional[str]             = Field("iii-ai-flow-hub-api", env="IAPP_NAME")
    IAPP_VERSION: Optional[str]          = Field("1.0.1", env="IAPP_VERSION")

    ENVIRONMENT: Optional[str]           = Field("production", env="ENVIRONMENT")
    CLUSTER: Optional[str]               = Field(None, env="cluster")
    NAMESPACE: Optional[str]             = Field(None, env="namespace")
    EXTERNAL: Optional[str]              = Field(None, env="external")
    WORKSPACE: Optional[str]             = Field(None, env="workspace")
    ENSAAS_SERVICES: Optional[dict]      = Field(None, env="ENSAAS_SERVICES")

    MONGODB_URL: Optional[str]           = Field(None, env="MONGODB_URL")
    MONGODB_DATABASE: Optional[str]      = Field(None, env="MONGODB_DATABASE")
    MONGODB_USERNAME: Optional[str]      = Field(None, env="MONGODB_USERNAME")
    MONGODB_PASSWORD: Optional[str]      = Field(None, env="MONGODB_PASSWORD")
    MONGODB_PASSWORD_FILE: Optional[str] = Field(None, env="MONGODB_PASSWORD_FILE")
    MONGODB_AUTH_SOURCE: Optional[str]   = Field(None, env="MONGODB_AUTH_SOURCE")
    MONGODB_AUTHMECHANISM: Optional[str] = Field("SCRAM-SHA-1", env="MONGODB_AUTHMECHANISM")

    MINIO_HOST: Optional[str]     = Field(None, env="MINIO_HOST")
    MINIO_USER: Optional[str]     = Field(None, env="MINIO_USER")
    MINIO_PASSWORD: Optional[str] = Field(None, env="MINIO_PASSWORD")
    BUCKET_NAME: Optional[str]    = Field("model", env="BUCKET_NAME")

    III_DATAFABRIC_API_URL: Optional[str]     = Field(None, env="III_DATAFABRIC_API_URL")
    III_AI_FLOW_HUB_ENGINE_URL: Optional[str] = Field(None, env="III_AI_FLOW_HUB_ENGINE_URL")
    
    class Config:
        env_file = ".env"

class Config(Settings):

    os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = "python"
    
    if Settings().ENSAAS_SERVICES is not None:
        ENSAAS_SERVICES = Settings().ENSAAS_SERVICES
        if 'mongodb' in ENSAAS_SERVICES:
            MONGODB_URL = ENSAAS_SERVICES.get('mongodb')[0].get('credentials').get('externalHosts')
            MONGODB_DATABASE = ENSAAS_SERVICES.get('mongodb')[0].get('credentials').get('database')
            MONGODB_USERNAME = ENSAAS_SERVICES.get('mongodb')[0].get('credentials').get('username')
            MONGODB_PASSWORD = ENSAAS_SERVICES.get('mongodb')[0].get('credentials').get('password')
            MONGODB_AUTH_SOURCE = MONGODB_DATABASE
    if Settings().MONGODB_PASSWORD == None and Settings().MONGODB_PASSWORD_FILE is not None:
        existence = os.path.exists(Settings().MONGODB_PASSWORD_FILE)
        if existence:
            MONGODB_PASSWORD = open(Settings().MONGODB_PASSWORD_FILE).read().rstrip('\n')

    # MDB COLL LIST
    MDB_DATA_INFO     = "iafh.data.info"
    MDB_TASK_INFO     = "iafh.task.info"
    MDB_TASK_DETAIL   = "iafh.task.info.detail"
    MDB_MODEL_REPO    = "iafh.model.repo"
    MDB_MODEL_INFO    = "iafh.model.info"
    MDB_MODEL_DETAIL  = "iafh.model.info.detail"

@lru_cache()
def get_configs():
    configs = Config()
    logging.basicConfig(level=logging.INFO)
    config_vars = vars(configs)
    for key, value in config_vars.items():
        if key.isupper() and key not in ("ENSAAS_SERVICES", "OPENAI_API_KEY") and value is not None:
            logging.info(f"[ENV]  {key} ok ... : {value}")

    return configs

configs = get_configs() 