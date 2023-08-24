from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from config import configs as p
from app.routers import router_init
from app.logs import log_init, sys_log

def conf_init(app):
    sys_log.info(msg=f'Start III Ai Flow Hub service with {p.ENVIRONMENT} environment.')

def create_app():

    tags_metadata = [
        {
            "name": "Root",
            "description": "",
        },
        {
            "name": "Services",
            "description": "Operations with users. The **login** and **user/me** logic is also here.",
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
            "name": "Model Repo Management",
            "description": ""
        },
        {
            "name": "Deploy Management",
            "description": ""
        }
    ]

    app = FastAPI(
        title="III Ai Flow Hub (IAFH)(資策會智能流中心) Platform User Module Documentation.",
        description=f"II Ai Flow Hub (IAFH)(資策會智能流中心)  - Efficient AutoML For Everyone.",
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