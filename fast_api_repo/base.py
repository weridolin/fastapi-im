from pydantic import BaseModel
from typing import Any,Optional,Dict

class IMBaseModel(BaseModel):
    class Config:
        orm_mode=True


class BaseResponse(IMBaseModel):
    message:Optional[str]=None
    status_code:int=200
    code:int=0
    data:Any=None

class ErrorContext(BaseModel):
    status_code: int
    detail: Any = None
    headers: Optional[Dict[str, Any]] = None

class BaseErrResponse(BaseModel):
    code:int=1
    data:ErrorContext

