## socket io 的消息格式
from pydantic import BaseModel
from enum import Enum, IntEnum
from typing import Any,Optional,Union
from datetime import datetime
from typing import List
from database.schema import UserSchema



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
    MSGACK="msgAck" #客户端确认收到的消息的格式
    GROUPNEWNUMBER="groupNewNumber"
    GROUPEXISTNUMBER="groupExistNumber"
    USERINFOCHANGE="userInfoChange" #用户资料改变
    ADDFRIEND="addFriend" #新增好友申请
    # DELFRIEND="delFriend" #删除好友
    FRIENDACCEPT="friendAccept" #好友添加被接受
    FRIENDREFUSED="friendRefuse"#好友添加被拒绝

    # BLACKLISTDEL="blackListDel"#从黑名单中移除


class MessageContentType(IntEnum):
    text=1

class BaseFrame(BaseModel):
    type:str=FrameType.UNDEFINED.value
    data:Any=None

class MessagePayLoad(BaseModel):
    ## 群消息时,msg_to为空，单聊时,group_id为None
    msg_from:int
    msg_to:Optional[int]=None
    msg_content:str
    msg_type:MessageContentType=MessageContentType.text
    group_id:Optional[int]=None
    send_time:Optional[int]=None
    created:Optional[int]=None 
    last_update:Optional[int]=None 

class AddFriendPayLoad(BaseModel):
    type:str=FrameType.ADDFRIEND.value
    user:UserSchema

class AcceptFriendPayLoad(AddFriendPayLoad):
    type:str=FrameType.FRIENDACCEPT.value

class RefuseFriendPayLoad(AddFriendPayLoad):
    type:str=FrameType.FRIENDREFUSED.value

class UserInfoChangePayload(BaseModel):
    type:str=FrameType.USERINFOCHANGE.value
    user:UserSchema

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
        消息支持多种类型，除了基本的消息类型，还包括
    """
    type:str=FrameType.MESSAGE.value
    data: Union[MessagePayLoad,AcceptFriendPayLoad,AddFriendPayLoad,RefuseFriendPayLoad,UserInfoChangePayload]

    
class MessageResponse(BaseFrame):
    result:bool=False

class MessageResponseFrame(BaseFrame):
    type:str=FrameType.RESPONSE.value
    data:MessageResponse

class MessageAckFrame(BaseFrame):
    """
        收到消息确认返回
    """
    type:str=FrameType.MSGACK.value
    msg_ids:List[str]=list()
    user_id:int
    username:str

## 拉取的消息格式
class MessagePulled(BaseFrame):
    """

    """
    type:str=FrameType.MESSAGE.value
    data:MessagePayLoad
    msg_id:str

# class Groupe
