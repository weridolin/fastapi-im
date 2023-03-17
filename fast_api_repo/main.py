from fastapi import FastAPI
from socketio import AsyncServer
import socketio
from fastapi_socketio import SocketManager
import uvicorn
from auth.apis import auth_router
from message.apis import msg_router
from group.apis import group_router
from fastapi import Request,HTTPException
from fastapi.responses import JSONResponse
from fast_api_repo.base import BaseErrResponse,ErrorContext

app = FastAPI()

@app.exception_handler(HTTPException)
def error_wrapper(request,exception:HTTPException):
    ## custom error schema 
    return JSONResponse(
        status_code=exception.status_code,
        content=BaseErrResponse(
            data=ErrorContext(
                status_code= exception.status_code,
                detail=exception.detail,
                headers=exception.headers
            )
        ).dict()
    )

app.include_router(
    router=auth_router,
    tags=["auth"],## swagger接口文档tags
    prefix="/auth",
)
app.include_router(
    router=msg_router,
    tags=["message"],
    prefix="/message"
)
app.include_router(
    router=group_router,
    tags=["group"],
    prefix="/group"
)


# sio =  AsyncServer(async_mode='asgi')

# @sio.event(namespace='/chat')
# def connect(sid, environ, auth):
#     print('connect ', sid)

# @sio.event(namespace='/chat')
# def disconnect(sid):
#     print('disconnect ', sid)

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

# app.mount("/",socketio.ASGIApp(sio,socketio_path="chat"))
