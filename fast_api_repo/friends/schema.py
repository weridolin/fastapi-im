from fast_api_repo.base import BaseResponse
from pydantic import BaseModel

class AddFriendRequest(BaseModel):
    # data=
    friend_user_id:int