## socket io 的消息格式
from pydantic import BaseModel
from enum import Enum, IntEnum
from typing import Any,Optional
from datetime import datetime
from typing import List



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

## socket io 自定义 event 类型
class FrameType(Enum):
    HEARTBEAT="heartbeat"
    UNDEFINED="undefined"
    MESSAGE="message"
    RESPONSE="response"
    MSGACK="msgack" #客户端确认收到的消息的格式
    
class MessageContentType(IntEnum):
    text=1

class BaseFrame(BaseModel):
    type:str=FrameType.UNDEFINED.value
    data:Any=None

class MessagePayLoad(BaseModel):
    msg_from:int
    msg_to:int
    msg_content:str
    msg_type:MessageContentType=MessageContentType.text
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
    type:str=FrameType.HEARTBEAT.value
    data:UserInfo

class Message(BaseFrame):
    """
        {
            "type":2,
            "data":{
                "msg_from":10,
                "msg_to":11,
                "msg_content":"test",
                "msg_type":1,
                "group_id":null,
                "send_time":1679275312,
                "created":1679275312, 
                "last_update":1679275312
            }
        }
    """
    type:str=FrameType.MESSAGE.value
    data:MessagePayLoad

class MessageResponse(BaseFrame):
    result:bool=False

class MessageResponseFrame(BaseFrame):
    type:str=FrameType.RESPONSE.value
    data:MessageResponse

class MessageAckFrame(BaseFrame):
    type:str=FrameType.MSGACK.value
    msg_ids:List[str]=list()
    user_id:int
    username:int
    

