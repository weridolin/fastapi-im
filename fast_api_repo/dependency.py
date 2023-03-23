from fast_api_repo.socketio_proxy import SocketioProxy


__sio = SocketioProxy(server_name="test")

async def get_sio():
    if not __sio.sio.connected:
        await __sio.start()
    return __sio