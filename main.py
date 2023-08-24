import uvicorn
from app import create_app

app =  create_app()

if __name__ == '__main__':

    uvicorn.run( app="app:create_app", host='0.0.0.0', port=5000, workers=1, loop="asyncio", reload=False, timeout_keep_alive=36, factory=True)
