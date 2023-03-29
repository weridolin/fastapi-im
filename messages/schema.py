## socket io 的消息格式
from pydantic import BaseModel
from enum import Enum, IntEnum
from typing import Any,Optional,Union
from datetime import datetime
from typing import List
from database.schema import UserSchema,GroupSchema


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

class FrameType(Enum):
    ## socket io 自定义 event 类型
    HEARTBEAT="heartbeat"
    UNDEFINED="undefined"
    MESSAGE="message"
    DeliverResult="DeliverResult"
    MSGACK="msgAck" #客户端确认收到的消息的格式

class MessageType(Enum):
    ## Message的类型
    MESSAGE="message"## 普通消息发送
    GROUPNEWNUMBER="groupNewNumber"
    GROUPEXISTNUMBER="groupExistNumber"
    USERINFOCHANGE="userInfoChange" #用户资料改变
    ADDFRIEND="addFriend" #新增好友申请
    # DELFRIEND="delFriend" #删除好友 todo 删除方不删除？
    FRIENDACCEPT="friendAccept" #好友添加被接受
    FRIENDREFUSED="friendRefuse"#好友添加被拒绝

    # BLACKLISTDEL="blackListDel"#从黑名单中移除
    ## Message的类型
    GROUPINFOCHANGE="groupInfoChange" # 群信息改变，包括群名，公告，群介绍
    GROUPCREATE="groupCreate"
    GROUPDELETE="groupDelete"

class MessageContentType(IntEnum):
    text=1

class BaseFrame(BaseModel):
    type:str=FrameType.UNDEFINED.value
    data:Any=None

class MessagePayLoad(BaseModel):
    ## 群消息时,msg_to为空，单聊时,group_id为None
    type = MessageType.MESSAGE.value
    msg_from:int
    msg_to:Optional[int]=None
    msg_content:str
    msg_type:MessageContentType=MessageContentType.text
    group_id:Optional[int]=None
    send_time:Optional[int]=None
    created:Optional[int]=None 
    last_update:Optional[int]=None 

class AddFriendPayLoad(BaseModel):
    type:str=MessageType.ADDFRIEND.value
    friend_info:UserSchema # 添加的好友信息
    from_id:int # 发出该消息的用户id
    to_id:int # 接受该消息的用户id
    request_id:int # 该请求对应的记录ID


class AcceptFriendPayLoad(AddFriendPayLoad):
    type:str=MessageType.FRIENDACCEPT.value


class RefuseFriendPayLoad(AddFriendPayLoad):
    type:str=MessageType.FRIENDREFUSED.value

class UserInfoChangePayload(BaseModel):
    type:str=MessageType.USERINFOCHANGE.value
    user:UserSchema

##### 群聊相关
class GroupInfoChangePayload(BaseModel):
    type:str=MessageType.GROUPINFOCHANGE.value
    group_id:int
    group_number_list:List[int]
    group_name:Optional[str]=None #群名称
    group_info:Optional[str]=None # 群介绍
    notification:Optional[str]=None # 群通知
    user:UserSchema # 操作用户

class GroupCreatePayload(BaseModel):
    type:str=MessageType.GROUPCREATE.value
    init_member_list:List[int]
    user:UserSchema # 操作用户
    group:GroupSchema

class GroupDeletePayload(BaseModel):
    type:str=MessageType.GROUPDELETE.value
    user:UserSchema # 操作用户
    group:GroupSchema 
    group_number_list:List[int]


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
        消息支持多种类型，除了基本的消息类型
    """
    type:str=FrameType.MESSAGE.value
    ## todo 拆开
    data: Union[MessagePayLoad,AcceptFriendPayLoad,AddFriendPayLoad,RefuseFriendPayLoad,GroupInfoChangePayload,GroupCreatePayload,GroupDeletePayload]

    
class MessageAckFrame(BaseFrame):
    """
        收到消息确认返回
    """
    type:str=FrameType.MSGACK.value
    msg_ids:List[str]=list()
    user_id:int
    username:str


class MessageDeliverResult(BaseFrame):
    ## 消息投递结果
    type:str=FrameType.DeliverResult.value
    result:bool=False
    data:Optional[Any]=None
    msg:Optional[str]=None
    

## 拉取的消息格式
class MessagePulled(BaseFrame):
    """

    """
    type:str=FrameType.MESSAGE.value
    data:Union[MessagePayLoad,AcceptFriendPayLoad,AddFriendPayLoad,RefuseFriendPayLoad,UserInfoChangePayload]
    msg_id:str



# class GroupMessageFrame(BaseFrame):
#     type=FrameType.MESSAGE.value
#     data:Optional[GroupInfoChangePayload]=None
    
