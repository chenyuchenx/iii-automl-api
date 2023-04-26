from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from config import configs as p
from app.routers import router_init
from app.logs import log_init, sys_log

def conf_init(app):
    sys_log.info(msg=f'Start app with {p.ENVIRONMENT} environment')
    if p.ENVIRONMENT == 'production':
        app.docs_url = None
        app.redoc_url = None
        app.debug = False

def create_app():

    tags_metadata = [
        {
            "name": "Root",
            "description": " Operations with users. The **login** and **tokenvalidation** logic is also here.",
        },
        {
            "name": "Services",
            "description": " Get inAppInfos && Get service secret && Search quota.",
        },
        {
            "name": "Data Management",
            "description": ""
        },
        {
            "name": "Task Management",
            "description": ""
        },
        {
            "name": "Model Management",
            "description": ""
        },
        {
            "name": "Deploy Management",
            "description": ""
        }
    ]

    app = FastAPI(
        title="Industrial AI (IAI) Management API - Inference Server",
        description=f"Industrial AI (IAI) Inference Platform User Module Documentation.",
        version=f"{p.IAPP_VERSION}",
        openapi_tags=tags_metadata
    )

    conf_init(app)

    log_init()

    router_init(app)

    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app