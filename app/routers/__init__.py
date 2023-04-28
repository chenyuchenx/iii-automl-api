from fastapi import Query, HTTPException, Response, Request
from config import configs as p
from app.src import sched
from .repo import router as repo_router
from .task import router as infer_router
from .dataset import router as data_router
from .auth import app as auth_routh
import os, sys

def router_init(app):

    @app.on_event('startup')
    def init_data():
        sched.__init__()

    @app.get("/", tags=['Root'])
    def read_root(*, request: Request):
        print(request.headers)
        return f"The {p.IAPP_NAME_LOWER}-api is already working."
    
    @app.get("/images/icon.svg", tags=['Root'])
    def read_image(*, request: Request):
        try:
            if hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.abspath(".")
            image_path = os.path.join(base_path, "public", "logo.svg")
            with open(image_path, 'rb') as f:
                image = f.read()
                return Response(content=image, media_type="image/svg+xml")
        except OSError as e:
            raise HTTPException(status_code=404, detail=f"{e}")
    
    app.include_router(auth_routh, prefix='', tags=['Services'])
    app.include_router(data_router, prefix='/data', tags=['Data Management'])
    app.include_router(infer_router, prefix='/task', tags=['Task Management'])
    app.include_router(repo_router, prefix='/repo', tags=['Model Repo Management'])

    #app.include_router(task_router, prefix='/api/task', tags=['task'] )
    #app.include_router(forward_router, prefix='/api/forwardinginfo', tags=['dataforward'])