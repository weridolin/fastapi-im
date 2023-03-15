from fast_api_repo.base import IMBaseModel,BaseModel,BaseResponse
from database.schema import UserSchema

class LoginRequest(BaseModel):
    count:str
    password:str

class UserWithToken(UserSchema):
    access_token:str
    refresh_token:str

class LoginResponse(BaseResponse):
    data:UserWithToken

