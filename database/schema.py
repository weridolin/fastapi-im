from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class SchemaMixin(object):
    class Config:
        orm_mode=True
        
    created:datetime=datetime.now
    last_update:Optional[datetime]=None


class UserSchema(BaseModel,SchemaMixin):
    username:Optional[str] =None
    password:str
    email:str
    telephone:str
    avatar:str
    age:int
    sex:int


class UserFriendShipSchema(BaseModel,SchemaMixin):
    user_id:int
    friend_id:int
    friend_group:str
    current_contact_time:datetime
    friend_nickname:str
    relationship:int=1


class UserGroupShipSchema(BaseModel,SchemaMixin):
    user_id:int
    group_id:int
    current_contact_time:str
    group_nickname:str


class GroupSchema(BaseModel,SchemaMixin):
    group_name:str
    creator_id:int
    created_time:datetime
    owner_id:int
    announcement:str


class MessageSchema(BaseModel,SchemaMixin):
    msg_from:int
    msg_to:int
    msg_content:str
    msg_type:int=0
    send_time:datetime