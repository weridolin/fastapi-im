## socket io 的消息格式
from pydantic import BaseModel
from enum import Enum, IntEnum
from typing import Any,Optional
from datetime import datetime


SENDRESPONSE = "send_response"

class UserState(IntEnum):
    online=0
    leave=1
    cloaking=2
    busy=4
    offline=5

class UserInfo(BaseModel):
    state:UserState = UserState.offline
    user_id:int
    sid:str # 若用户在线,对应的会话ID

class FrameType(IntEnum):
    heartbeat=1
    undefined=-1
    message=2
    response=3

class ContentType(IntEnum):
    text=1

class BaseFrame(BaseModel):
    type:FrameType=FrameType.undefined
    data:Any=None

class MessagePayLoad(BaseModel):
    msg_from:int
    msg_to:int
    msg_content:str
    msg_type:ContentType=ContentType.text
    group_id:Optional[int]=None
    send_time:Optional[int]=None
    created:Optional[int]=None 
    last_update:Optional[int]=None 

class HeartBeatFrame(BaseFrame):
    """
    {
        "type":1,
        "data":{
        "state":0,
        "user_id":10 
        }
    }
    """
    type=FrameType.heartbeat
    data:UserInfo

class Message(BaseFrame):
    type:FrameType=FrameType.message
    data:MessagePayLoad



class MessageResponse(BaseFrame):
    result:bool=False

class MessageResponseFrame(BaseFrame):
    type:FrameType=FrameType.response
    data:MessageResponse
