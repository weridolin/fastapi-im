from fast_api_repo.base import BaseResponse,IMBaseModel
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GetMessageHistoryRequest(BaseModel):
    msg_to:int

class MessagePayLoad(IMBaseModel):
    id:int
    msg_from:int
    msg_to:Optional[int]=None
    msg_content:str
    group_id:Optional[int]=None
    send_time:Optional[datetime]=None
    created:Optional[datetime]=None 
    last_update:Optional[datetime]=None