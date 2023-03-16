import sys
print(sys.path)
from fastapi import FastAPI
from socketio import AsyncServer
import socketio
from fastapi_socketio import SocketManager
import uvicorn
from auth.apis import auth_router
from message.apis import msg_router
from group.apis import group_router

app=FastAPI()
app.include_router(
    router=auth_router,
    tags=["auth"],## swagger接口文档tags
    prefix="auth",
)
app.include_router(
    router=msg_router,
    tags=["message"],
    prefix="message"
)
app.include_router(
    router=group_router,
    tags=["group"],
    prefix="group"
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
