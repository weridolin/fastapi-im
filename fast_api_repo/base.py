from pydantic import BaseModel
from typing import Any

class IMBaseModel(BaseModel):
    class Config:
        orm_mode=True


class BaseResponse(IMBaseModel):
    message:str=None
    status_code:int=200
    code:int=0
    data:Any=None