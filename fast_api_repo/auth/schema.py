from fast_api_repo.base import IMBaseModel,BaseModel,BaseResponse
from database.schema import UserSchema
from datetime import datetime
class LoginRequest(BaseModel):
    count:str
    password:str

class UserWithToken(UserSchema):
    access_token:str
    refresh_token:str

class LoginResponse(BaseResponse):
    data:UserWithToken

class RegisterForm(BaseModel):
    username:str
    password:str
    email:str


class JWTPayLoad(BaseModel):
    exp: datetime
    sub: str="access"
    username:str
