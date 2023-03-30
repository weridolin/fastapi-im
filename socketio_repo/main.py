import socketio
from settings import get_app_settings
from database.jwt import get_payload_from_token
from fast_api_repo.auth.schema import JWTPayLoad
from socketio.exceptions import ConnectionRefusedError
import traceback
from settings import get_app_settings
import aioredis
from utils.redis_key import RedisKey
from messages.schema import (    
        UserInfo,
        UserState,
        HeartBeatFrame,
        Message,
        FrameType,
        MessageAckFrame,
        MessagePulled,
        MessageType,
        MessageDeliverResult
    )
from typing import Any,List
from aioredis.exceptions import ResponseError
import json
from database.base import get_repository
from database.repositories.message import MessageRepository
from database.repositories.friends import FriendShipRepository
from utils.serializer import JsonEncoderWithTime


mgr = socketio.AsyncRedisManager(get_app_settings().REDIS_DSN)
sio = socketio.AsyncServer(
        async_mode='asgi',
        client_manager=mgr
    )
app = socketio.ASGIApp(sio,socketio_path="/chat")

class ImNameSpace(socketio.AsyncNamespace):

    app_settings = get_app_settings()
    msg_repo:MessageRepository = MessageRepository()
    friend_ship_repo:FriendShipRepository = FriendShipRepository()

    def __init__(self, namespace=None):
        super().__init__(namespace)
        self.redis = aioredis.from_url(
        self.app_settings.REDIS_DSN ,encoding="utf-8", decode_responses=True)
        self.sid_user_id_dict=dict()

    async def on_connect(self, sid, environ,data=None):
        # 处理内部服务直接通过
        if data and data["id"]=="9527":
            print("(socket io) internal service connect")
            return

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
                    ex=60*60*24 #TODO 超过3s没发送心跳，默认已经掉线
                )

                ## 获取登录用户消息队列里面未读取的数据
                try:
                    await self.pull_new_message(sid=sid,payload=payload)
                except ResponseError as exc:
                    if "NOGROUP" in str(exc):
                        print(f"(socket io) client:{payload.username}({payload.user_id}) has no create msg channel")
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
        print(f"receive client:{self.sid_user_id_dict.get(sid)} message ->",message)

        if message.data.type == MessageType.MESSAGE.value:
            ## 普通推送消息先入库
            _ = await self.msg_repo.create_message(message=message.data)
            if message.data.group_id:
                ### 处理群消息
                return await self.handle_group_message(msg=message)
            else:
                ### 处理1对1
                #### 1对1发送器前先确认下好友关系
                if  not await self.friend_ship_repo.is_friend(msg_from=message.data.msg_from,msg_to=message.data.msg_to):
                    return MessageDeliverResult(
                        msg="对方还不是您的好友!投递失败!"
                    ).dict()
                
                return await self.handle_single_message(msg=message,msg_to=message.data.msg_to) 

        elif message.data.type == MessageType.ADDFRIEND.value:
            return await self.handle_addFriend(msg=message)

        elif message.data.type == MessageType.FRIENDACCEPT.value: 
            return await self.handle_friendAccept(msg=message)
        
        elif message.data.type == MessageType.FRIENDREFUSED.value:
            return await self.handle_friendRefuse(msg=message)

        elif message.data.type == MessageType.GROUPINFOCHANGE.value:
            return await self.handle_groupInfoChange(msg=message)

        elif message.data.type == MessageType.GROUPCREATE.value:
            return await self.handle_groupCreate(msg=message)

        elif message.data.type == MessageType.GROUPDELETE.value:
            return await self.handle_groupDelete(msg=message)
    
        elif message.data.type == MessageType.GROUPNUMBERINVITE.value:
            return await self.handle_groupNumberInvite(msg=message)

    async def on_msgAck(self,sid,data:MessageAckFrame,*args):
        if isinstance(data,dict):
            msg=MessageAckFrame.parse_obj(data)
        else:
            msg=MessageAckFrame.parse_raw(data)
        # for id in msg.msg_ids:
        await self.redis.xack(
            RedisKey.user_msg_channel(user_id=msg.user_id),
            RedisKey.user_msg_channel_groups_name(user_id=msg.user_id,type="PC"),
            *msg.msg_ids
        )
        print("ack message ids ->",msg.msg_ids)

    async def handle_group_message(self,msg:Message):
        ## 1.先获取所有的群成员

        ## 2.对每个成员按照 一对一处理
        ...

    async def handle_single_message(self,msg:Message,msg_to:int):
        ##查询接收的用户在线状态
        try:
            user_to:UserInfo = await self.redis.get(
                RedisKey.user_info_key(user_id=msg_to)
            )
            if user_to:
                user_to = json.loads(user_to)
            if user_to and user_to["state"]!=UserState.offline and user_to["sid"] in self.sid_user_id_dict:
                ## 用户在线
                print(">>> 用户在线")
                await sio.emit(
                    event= FrameType.MESSAGE.value,
                    data=msg.json(),
                    namespace="/im",
                    to=user_to["sid"]
                )
            else:
                ## 未在线,推送到对应的mq/用户一对一写消息队列
                ### 先写到对应的一对一消息信道
                print(">>> 用户不在线")
                await self.redis.xadd(
                    name=RedisKey.user_msg_channel(
                        user_id=msg_to
                    ),
                    fields={"data":msg.data.json()},
                    id="*"  # TODO id设置为消息ID？必须递增
                )
                ### 创造PC端的消费者组,如果报错，说明已经存在，跳过,消费者会在读取消息的时候去创建
                # TODO 移动端
                await self.redis.xgroup_create(
                    name=RedisKey.user_msg_channel(
                        user_id=msg_to
                    ),
                    groupname=RedisKey.user_msg_channel_groups_name(
                        user_id=msg_to,
                        type="PC"
                    ),
                    id="0-0"
                )
        except Exception as exc:
            if "BUSYGROUP" in str(exc):
                print("consumer is already exist")
            else:
                # return MessageDeliverResult(
                #     msg=str(exc)
                # ).dict()
                raise
        # return MessageDeliverResult(
        #     result=True,
        #     msg="消息投递成功!"
        # ).dict()

    async def pull_new_message(self,sid,payload:JWTPayLoad):
        ## 获取客户端未确认收到的消息.
        ### 1.先获取group里面未ack的消息，即为 pel队列. xpending
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
            print("(socket io)  pending list",pending_list)
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
            print("(socket io)  msg list",msg_list)
        print("(socket io) res",res)
        if res:
            res_format = [
                MessagePulled.parse_obj(
                    {               
                        "msg_id":msg[0],
                        "data":json.loads(msg[1]["data"])
                    }
                ).dict() for msg in res
            ]
            ## 把新消息发送给客户端，客户端返回收到的消息id 
            await sio.emit(
                event= FrameType.MESSAGE.value,
                data=json.dumps(res_format,ensure_ascii=False,cls=JsonEncoderWithTime),
                namespace="/im",
                to=sid
            )

    async def handle_addFriend(self,msg:Message):
        print("(socket io) add friend request")
        try:
            await self.handle_single_message(msg=msg,msg_to=msg.data.to_id)
        except Exception as exc:
            return False,exc.__str__()
        return True,None

    async def handle_friendAccept(self,msg:Message):
        print("(socket io) accept friend request")
        try:
            await self.handle_single_message(msg=msg,msg_to=msg.data.to_id)
        except Exception as exc:
            return False,exc.__str__()
        return True,None

    async def handle_friendRefuse(self,msg:Message):
        print("(socket io) refuse friend request")
        try:
            await self.handle_single_message(msg=msg,msg_to=msg.data.to_id)
        except Exception as exc:
            return False,exc.__str__()
        return True,None

    async def handle_groupInfoChange(self,msg:Message):
        try:
            for msg_to in msg.data.group_number_list:
                await self.handle_single_message(msg=msg,msg_to=msg_to)
        except Exception as exc:
            return False,exc.__str__()
        return True,None

    async def handle_groupCreate(self,msg:Message):
        try:
            for msg_to in msg.data.init_member_list:
                await self.handle_single_message(msg=msg,msg_to=msg_to)
        except Exception as exc:
            return False,exc.__str__()
        return True,None       

    async def handle_groupDelete(self,msg:Message):
        try:
            for msg_to in msg.data.group_number_list:
                await self.handle_single_message(msg=msg,msg_to=msg_to)
        except Exception as exc:
            return False,exc.__str__()
        return True,None            

    async def handle_groupNumberInvite(self,msg:Message):
        try:
            for msg_to in msg.data.new_number_list:
                await self.handle_single_message(msg=msg,msg_to=msg_to)
        except Exception as exc:
            return False,exc.__str__()
        return True,None            


sio.register_namespace(ImNameSpace('/im'))


    