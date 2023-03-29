from pydantic import BaseModel,validator
from datetime import datetime
from typing import Optional,List
class SchemaMixin(BaseModel):
    class Config:
        orm_mode=True
        
    created:Optional[datetime]=None
    last_update:Optional[datetime]=None

    @validator('created', pre=True, always=True)
    def set_create_now(cls, v):
        return v or datetime.now()

class UserSchema(SchemaMixin):
    id:int
    username:Optional[str] =None
    # password:str
    email:Optional[str] =None
    telephone:Optional[str] =None
    avatar:Optional[str] =None
    age:Optional[str] =None
    sex:Optional[str] =None


class UserFriendShipSchema(SchemaMixin):
    user_id:int
    friend_id:int
    friend_group:str
    current_contact_time:datetime
    friend_nickname:str
    relationship:int=1


class UserGroupShipSchema(SchemaMixin):
    user_id:int
    group_id:int
    current_contact_time:str
    group_nickname:str

######## 群相关
class GroupSchema(SchemaMixin):
    id:int
    group_name:str
    creator_id:int
    created_time:datetime
    owner_id:int
    notification:str
    notification_update_time:datetime
    notification_user_id:int
    notification_user:Optional[UserSchema]=None
    group_intro:str
    status:int=0
    max_member_count:int=50
    member_count:Optional[int]=0

class GroupMemberShipSchema(SchemaMixin):
    id:int
    user_id:int
    user:Optional[UserSchema]=None
    group_id:int
    group:Optional[GroupSchema]=None
    current_contact_time:datetime
    group_nickname:str
    invited_user_id:int
    invited_user:Optional[UserSchema]=None
    role:int=0
    join_time:datetime

class GetGroupInfoRequest(BaseModel):
    group_id_list:List[int]

class CreateGroupRequest(BaseModel):
    group_name:str
    group_intro:str
    init_member_list: List[int]
    notification: Optional[str]=None

class GroupInfoUpdateRequest(BaseModel):
    group_name:Optional[str]=None
    notification:Optional[str]=None
    group_intro:Optional[str]=None
    # needVerification为群验证 0为申请需要同意 邀请直接进 1为所有人进群需要验证，除了群主管理员邀请进群 2为直接进群

####### message 相关
class MessageSchema(SchemaMixin):
    msg_from:int
    msg_to:int
    msg_content:str
    msg_type:int=0
    send_time:datetime