from fastapi import APIRouter
from fast_api_repo.friends.schema import AddFriendRequest
from fastapi import  Depends
from database.jwt import create_access_token_for_user,get_current_active_user
from database.base import get_repository
from database.repositories.friends import FriendShipRepository
from database.models.user import User
from fast_api_repo.dependency import get_sio

friend_router = APIRouter()

@friend_router.post(
    "",
    name="friend:add-friend",
)
async def add_friend(
    request_form:AddFriendRequest,
    user:User=Depends(get_current_active_user),
    friends_manager_repo:FriendShipRepository= Depends(get_repository(FriendShipRepository)),
    sio = Depends(get_sio)
):
    await friends_manager_repo.add_friend(
        request_user_id=user.id,
        friend_user_id=request_form.friend_user_id
    )




# from fastapi import Request
# from pydantic import BaseModel

# class Form(BaseModel):
#     field:str


# def interrupt(user_id,body_var,request:Request):
#     print(user_id,body_var,request)

# @friend_router.post(
#     "/test/{user_id}",
#     name="friend:add-friend",
# )
# async def test(
#     user_id:int,body_var:str,form:Form,
#     i=Depends(interrupt)
# ):
#     print(">>>>",user_id,body_var,form)
