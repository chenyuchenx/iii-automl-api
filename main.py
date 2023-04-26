from config import configs as p
from app.logs import sys_log
from app import create_app
import time, uvicorn, urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = create_app()

if __name__ == '__main__':

    # Server Start
    if p.IFP_SSL_ENABLE == True:
        uvicorn.run( app=create_app(), host='0.0.0.0', port=5000, workers=1, loop="asyncio", reload=False, ssl_keyfile=p.IFP_SSL_PRIVATE_KEY_FILE, ssl_certfile=p.IFP_SSL_CERTIFICATE_FILE)
    else:
        uvicorn.run( app=create_app(), host='0.0.0.0', port=5000, workers=1, loop="asyncio", reload=False)
