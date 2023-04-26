from pydantic import BaseSettings, Field
from functools import lru_cache
from typing import Optional
import logging, os, json

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """System configurations."""

    SKIP_TLS: Optional[bool]                = Field(False, env="SKIP_TLS")
    IFPS_TIME_OUT: Optional[int]            = Field(10, env="IFPS_TIME_OUT")
    IFP_SSL_ENABLE: Optional[bool]          = Field(False, env="IFP_SSL_ENABLE")
    IFP_SSL_CERTIFICATE_FILE: Optional[str] = Field(None, env="IFP_SSL_CERTIFICATE_FILE")
    IFP_SSL_PRIVATE_KEY_FILE: Optional[str] = Field(None, env="IFP_SSL_PRIVATE_KEY_FILE")

    IAPP_NAME: Optional[str]         = Field("ifps-inference-api", env="IAPP_NAME")
    IAPP_VERSION: Optional[str]      = Field("1.7.1.1", env="IAPP_VERSION")
    IAPP_NAME_CAPITAL: Optional[str] = Field(None, env="IAPP_NAME_CAPITAL")
    IAPP_NAME_LOWER: Optional[str]   = Field(None, env="IAPP_NAME_LOWER")
    IAPP_UI_URL: Optional[str]       = Field(None, env="IAPP_UI_URL")
    IAPP_API_URL: Optional[str]      = Field(None, env="IAPP_API_URL")

    L3_MODE: Optional[bool]           = Field(True, env="L3_MODE")
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

    IFP_DESK_PREFIX: Optional[str]          = Field("ifp-api-hub", env="IFP_DESK_PREFIX")
    IFP_DESK_URL: Optional[str]             = Field(None, env="IFP_DESK_UI_URL")
    IFP_DESK_API_URL: Optional[str]         = Field(None, env="IFP_DESK_API_URL")
    IFP_LICENSES_API_URL: Optional[str]     = Field(None, env="IFP_LICENSES_API_URL")
    IFPS_ETCD_BROKER_API_URL: Optional[str] = Field(None, env="IFPS_ETCD_BROKER_API_URL")
    IFPS_UDM_UI_URL: Optional[str]          = Field(None, env="IFPS_UDM_UI_URL")
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
    if Settings().L3_MODE and Settings().IFP_DESK_API_URL is None and Settings().EXTERNAL is not None:
        IFP_DESK_URL             = "https://pivot-api-hub-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL
        IFP_DESK_API_URL         = "https://pivot-api-hub-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL+"/graphql"
        IFP_EVENTNOTICE_API_URL  = "https://pivot-event-notice-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL
        IFP_MAINTENANCE_API_URL  = "https://maintenance-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL+"/api/v1/graphql"
    elif Settings().IFP_DESK_API_URL is None and Settings().EXTERNAL is not None:
        IFP_DESK_URL             = "https://"+Settings().IFP_DESK_PREFIX+"-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL
        IFP_DESK_API_URL         = "https://"+Settings().IFP_DESK_PREFIX+"-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL+"/graphql"
        IFP_EVENTNOTICE_API_URL  = "https://ifp-event-notice-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL
        IFP_MAINTENANCE_API_URL  = "https://maintenance-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL+"/api/v1/graphql"
    if Settings().IAPP_API_URL is None and Settings().EXTERNAL is not None:
        IAPP_UI_URL              = "https://ifps-inference-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL
        IAPP_API_URL             = "https://ifps-inference-api-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL
        IFPS_UDM_UI_URL          = "https://ifps-udm-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL
    else:
        IFPS_UDM_UI_URL          = "https://ifps-udm:5000"
        IAPP_UI_URL              = "https://ifps-inference:5000"
        IAPP_API_URL             = "https://ifps-inference-api:5000"
        IFP_EVENTNOTICE_API_URL  = "https://event-notice:5000"
        IFP_MAINTENANCE_API_URL  = "https://maintenance:5000"
    if Settings().IFPS_ETCD_BROKER_API_URL is None and Settings().EXTERNAL is not None:
        IFPS_ETCD_BROKER_API_URL = "https://ifps-inference-etcd-broker-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL
    if Settings().IFPS_DATAFABRIC_API_URL is None and Settings().EXTERNAL is not None:
        IFPS_DATAFABRIC_API_URL = "https://ifps-datafabric-api-"+Settings().NAMESPACE+"-"+Settings().CLUSTER+"."+Settings().EXTERNAL

    # global
    mongo_data_info           = "iii.data.info"

    mongo_kpi_metrics         = "iii.pre.metrics"
    mongo_pre_catalog         = "iii.pre.catalog"
    mongo_pre_user            = "iii.pre.user"
    mongo_pre_roles           = "iii.pre.roles"
    clientSecrets             = {}

    mongo_pre_edge_model     = "iii.pre.edge.model"
    mongo_pre_edge_server    = "iii.pre.edge.server"
    mongo_pre_edge_infer     = "iii.pre.edge.infer"

    mongo_pre_oee_kpi        = "iii.pre.oee_kpi"
    mongo_pre_oee_kpi_alert  = "iii.pre.oee_kpi_alert"
    
    
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