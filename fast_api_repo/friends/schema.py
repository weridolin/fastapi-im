from fast_api_repo.base import BaseResponse
from pydantic import BaseModel
from typing import Optional
class AddFriendRequest(BaseModel):
    # data=
    friend_user_id:int
    check_info:Optional[str]=None

class DealFriendAskRequest(BaseModel):
    request_id:int
    accept:bool=False
    refuse_reason:Optional[str]=None