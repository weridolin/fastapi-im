import socketio
from typing import Callable

class SocketioProxy:
    sio=socketio.AsyncClient(reconnection_attempts=100,logger=True)

    def __init__(self,server_name:str,ssl=False):
        self.ssl=ssl
        self.is_connect=False
    
    async def start(self):
        if not self.ssl:
            print(">>> connect to socketio service")
            ## TODO 根据name去获取？
            await self.sio.connect("http://127.0.0.1:8001",auth={"id":"9527"},socketio_path="/chat",namespaces=['/im'])
        

    def bind_event(self,event:str,callback:Callable):
        ...

    # @SocketioProxy.sio.on('connect')
    # async def on_connect(*args):
    #     print(">>> client on connect",args)

    # @SocketioProxy.sio.on('disconnect')
    # async def on_disconnect():
    #     print(">>> client on disconnect")

    # @SocketioProxy.sio.on('message')
    # async def on_message(data):
    #     print(">>> client on message ",data)

    