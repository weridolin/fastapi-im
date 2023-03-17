from pydantic import BaseModel,validator
from datetime import datetime
from typing import Optional
class SchemaMixin(BaseModel):
    class Config:
        orm_mode=True
        
    created:Optional[datetime]=None
    last_update:Optional[datetime]=None

    @validator('created', pre=True, always=True)
    def set_create_now(cls, v):
        return v or datetime.now()

class UserSchema(SchemaMixin):
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


class GroupSchema(SchemaMixin):
    group_name:str
    creator_id:int
    created_time:datetime
    owner_id:int
    announcement:str


class MessageSchema(SchemaMixin):
    msg_from:int
    msg_to:int
    msg_content:str
    msg_type:int=0
    send_time:datetime