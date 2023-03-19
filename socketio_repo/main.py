import socketio
from settings import get_app_settings
from database.jwt import get_payload_from_token
from fast_api_repo.auth.schema import JWTPayLoad
from socketio.exceptions import ConnectionRefusedError
import traceback
from settings import get_app_settings
import aioredis
from utils.redis_key import RedisKey
from messages.schema import UserInfo,UserState,HeartBeatFrame,Message,SENDRESPONSE,MessageResponse,MessageResponseFrame
from typing import Any

mgr = socketio.AsyncRedisManager(get_app_settings().REDIS_DSN)
sio = socketio.AsyncServer(
    async_mode='asgi',
    client_manager=mgr
    )
app = socketio.ASGIApp(sio)


class ImNameSpace(socketio.AsyncNamespace):

    app_settings = get_app_settings()

    def __init__(self, namespace=None):
        super().__init__(namespace)
        self.redis = aioredis.from_url(
        self.app_settings.REDIS_DSN ,encoding="utf-8", decode_responses=True)
        self.sid_user_id_dict=dict()

    async def on_connect(self, sid, environ):
        token = environ.get("HTTP_AUTHORIZATION",None)
        if token:
            try:
                payload:JWTPayLoad = get_payload_from_token(
                    app_setting=get_app_settings(),
                    token=token
                )
                print(f"(socket io) client:{payload.username}({payload.user_id}) connect")
                user_info:UserInfo = UserInfo(
                    state=UserState.online,
                    user_id=payload.user_id
                )
                self.sid_user_id_dict.update({
                    sid:payload.user_id
                })
                ## update redis user info
                await self.redis.set(
                    RedisKey.user_info_key(user_id=payload.user_id),
                    user_info.json(),
                    ex=5 # 超过3s没发送心跳，默认已经掉线

                )
            except Exception:
                # print(traceback.format_exc())
                raise ConnectionRefusedError("token is invalid")        
        else:
            raise ConnectionRefusedError("token cannot be none")

    async def on_disconnect(self, sid):
        try:
            await self.redis.delete(
                RedisKey.user_info_key(
                    user_id=self.sid_user_id_dict.pop(sid),
                    ),
            )
        except KeyError:
            pass
    
    async def on_heartbeat(self, sid, data:HeartBeatFrame,*args):
        heartbeat = HeartBeatFrame.parse_raw(data)
        print(f"receive client:{self.sid_user_id_dict.get(sid)} heartbeat",args)
        ## update redis user info
        await self.redis.set(
            RedisKey.user_info_key(user_id=heartbeat.data.user_id),
            heartbeat.data.json(),
            ex=5 # 超过3s没发送心跳，默认已经掉线
        )        

    async def on_message(self, sid, data:Message,*args):
        """
            接受到消息后,推送到mq,即返回成功,剩下的业务逻辑由不用的逻辑customer消费处理
        """
        message = Message.parse_raw(data)
        print(f"receive client:{self.sid_user_id_dict.get(sid)} message",message)
        if data.data.group_id:
            ...
            ### 处理群消息
        else:
            ### 处理1对1
            ...
    
    def handle_group_message(self,msg:Message):
        ...

    
    async def handle_single_message(self,msg:Message):
        user_to:UserInfo = await self.redis.get(
            RedisKey.user_info_key(user_id=msg.data.msg_to)
        )
        if user_to and user_to.state!=UserState.offline:
            ## 用户在线
            try:
                res = await sio.emit(
                    event= SENDRESPONSE,
                    data=MessageResponseFrame(
                        data=MessageResponse(
                            result=True
                        )
                    ),
                    to=user_to.sid
                )
            except Exception as exc:
                print(traceback.format_exc())
                
            ## 保存到数据库
            ...
        else:
            ## 未在线,推送到对应的mq，
            ...



sio.register_namespace(ImNameSpace('/im'))

# @sio.on('*',namespace="/im")
# def catch_all(*args,**kwargs):
#     print(args,kwargs)
    