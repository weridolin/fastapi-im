import socketio
from settings import get_app_settings
from database.jwt import get_payload_from_token
from fast_api_repo.auth.schema import JWTPayLoad
from socketio.exceptions import ConnectionRefusedError
import traceback
from settings import get_app_settings
import aioredis
from utils.redis_key import RedisKey
from messages.schema import UserInfo,UserState,HeartBeatFrame,Message,MessageResponse,MessageResponseFrame,FrameType,MessageAckFrame,MessagePulled,MessagePayLoad
from typing import Any 
from aioredis.exceptions import ResponseError
import json

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
                    user_id=payload.user_id,
                    sid=sid
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

                ## 获取登录用户消息队列里面未读取的数据
                try:
                    await self.pull_new_message(sid=sid,payload=payload)
                except ResponseError as exc:
                    if "NOGROUP" in str(exc):
                        print(f"client:{payload.username}({payload.user_id}) has no create msg channel")
                    else:
                        raise

            except Exception:
                print(traceback.format_exc())
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
        """"""
        message:Message = Message.parse_raw(data)
        print(f"receive client:{self.sid_user_id_dict.get(sid)} message")
        if message.data.group_id:
            ...
            ### 处理群消息
        else:
            ### 处理1对1
            await self.handle_single_message(msg=message) 
        return 

    async def on_msgack(self,sid,data:MessageAckFrame,*args):
        if isinstance(data,dict):
            msg=MessageAckFrame.parse_obj(data)
        else:
            msg=MessageAckFrame.parse_raw(data)
        print(">>>",msg)
        # for id in msg.msg_ids:
        await self.redis.xack(
            RedisKey.user_msg_channel(user_id=msg.user_id),
            RedisKey.user_msg_channel_groups_name(user_id=msg.user_id,type="PC"),
            *msg.msg_ids
        )
        print("ack message ids ->",msg.msg_ids)


    def handle_group_message(self,msg:Message):
        ...

    async def handle_single_message(self,msg:Message):
        user_to:UserInfo = await self.redis.get(
            RedisKey.user_info_key(user_id=msg.data.msg_to)
        )
        if user_to and user_to.state!=UserState.offline:
            ## 用户在线
            try:
                await sio.emit(
                    event= FrameType.MESSAGE.value,
                    data=msg.data.json(),
                    namespace="/im",
                    to=user_to.sid
                )
            except Exception as exc:
                print(traceback.format_exc())

            ## 保存到数据库
            ...
        else:
            ## 未在线,推送到对应的mq/用户一对一写消息队列
            ### 先写到对应的一对一消息信道
            await self.redis.xadd(
                name=RedisKey.user_msg_channel(
                    user_id=msg.data.msg_to
                ),
                fields={"data":msg.data.json()},
                id="*"  # TODO id设置为消息ID？必须递增
            )
            ### 创造PC端的消费者组,如果报错，说明已经存在，跳过,消费者会在读取消息的时候去创建
            # TODO 移动端
            try:
                await self.redis.xgroup_create(
                    name=RedisKey.user_msg_channel(
                        user_id=msg.data.msg_to
                    ),
                    groupname=RedisKey.user_msg_channel_groups_name(
                        user_id=msg.data.msg_to,
                        type="PC"
                    )
                )
            except Exception as exc:
                if "BUSYGROUP" in str(exc):
                    print("consumer is already exist")
                else:
                    raise

    async def pull_new_message(self,sid,payload:JWTPayLoad):
        ## 获取客户端未确认收到的消息.
        ### 1.先获取group里面未ack的消息，即为 pel队列.  xpending
        ### 2.再获取stream里面信息的消息 xreadgroup
        ### pel里面的消息肯定是在xreadgroup之前
        res=list()
        pending_list= await self.redis.xreadgroup(
            groupname=RedisKey.user_msg_channel_groups_name(
                user_id=payload.user_id,
                type="PC"
            ),
            consumername="consumer",
            streams={RedisKey.user_msg_channel(user_id=payload.user_id):0},
        )
        if pending_list:
            res.extend(pending_list[0][1])
            print(">>> pending list",pending_list)
        msg_list = await self.redis.xreadgroup(
            groupname=RedisKey.user_msg_channel_groups_name(
                user_id=payload.user_id,
                type="PC"
            ),
            consumername="consumer",
            streams={RedisKey.user_msg_channel(user_id=payload.user_id):">"}
        )  
        if msg_list:
            res.extend(msg_list[0][1])  # todo format res 
            print(">>> msg list",msg_list)
        res_format = [
            MessagePulled(
                msg_id=msg[0],
                data=MessagePayLoad.parse_raw(msg[1]["data"])
            ).dict() for msg in res
        ]
        ## 把新消息发送给客户端，客户端返回收到的消息id 
        res = await sio.emit(
            event= FrameType.MESSAGE.value,
            data=res_format,
            namespace="/im",
            to=sid
        )
        print(">>> send new message res ",res)        




sio.register_namespace(ImNameSpace('/im'))

# @sio.on('*',namespace="/im")
# def catch_all(*args,**kwargs):
#     print(args,kwargs)
    