from fast_api_repo.base import IMBaseModel,BaseModel,BaseResponse
from database.schema import UserSchema
from datetime import datetime
from typing import Optional


class LoginRequest(BaseModel):
    count:str
    password:str

class UserWithToken(BaseModel):
    access_token:str
    refresh_token:Optional[str]=None
    token_type:str= "bearer"
    user:UserSchema

class LoginResponse(BaseResponse):
    data:UserWithToken

class RegisterForm(BaseModel):
    username:str
    password:str
    email:str


class JWTPayLoad(BaseModel):
    user_id:int
    exp: int
    sub: str="access"
    username:str

class DelUserRequestForm(BaseModel):
    del_friend_id:int
