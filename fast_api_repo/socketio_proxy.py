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
            ## TODO 根据name去获取?auth白名单
            await self.sio.connect("http://127.0.0.1:8001",auth={"id":"9527"},socketio_path="/chat",namespaces=['/im'])
        

    def bind_event(self,event:str,callback:Callable):
        ...
    
    async def emit(self,event, data=None, namespace=None, callback=None):
        if not self.sio.connected:
            raise RuntimeError("socketio client is not connected")
        return await self.sio.emit(event, data=data, namespace=namespace, callback=callback)


    @sio.on('connect')
    async def on_connect(self,*args):
        print(">>> client on connect",args)

    @sio.on('disconnect')
    async def on_disconnect(self,*args):
        print(">>> client on disconnect")

    @sio.on('message')
    async def on_message(self,data):
        print(">>> client on message ",data)

    