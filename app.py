from fastapi import FastAPI
from socketio import AsyncServer
import socketio
from fastapi_socketio import SocketManager
import uvicorn

app=FastAPI()

sio =  AsyncServer(async_mode='asgi')

@sio.event(namespace='/chat')
def connect(sid, environ, auth):
    print('connect ', sid)

@sio.event(namespace='/chat')
def disconnect(sid):
    print('disconnect ', sid)

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.mount("/",socketio.ASGIApp(sio,socketio_path="chat"))
