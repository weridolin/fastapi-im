from fastapi import APIRouter
from fast_api_repo.friends.schema import AddFriendRequest,BaseResponse
from fastapi import  Depends
from database.jwt import get_current_active_user
from database.base import get_repository
from database.repositories.friends import FriendShipRepository
from database.repositories.user import UserRepository
from database.models.user import User
from fast_api_repo.dependency import get_sio,SocketioProxy
from messages.schema import Message,FrameType,AddFriendPayLoad,UserSchema
from asyncio.futures import Future
from fastapi import status

friend_router = APIRouter()

@friend_router.post(
    "",
    name="friend:add-friend",
    response_model=BaseResponse
)
async def add_friend(
    request_form:AddFriendRequest,
    user:User=Depends(get_current_active_user),
    friends_manager_repo:FriendShipRepository= Depends(get_repository(FriendShipRepository)),
    sio:SocketioProxy = Depends(get_sio),
    users_repo:UserRepository=Depends(get_repository(UserRepository)),

):
    record = await friends_manager_repo.add_friend(
        request_user_id=user.id,
        friend_user_id=request_form.friend_user_id
    )
    if record:
        fut:Future=Future()
        async def callback(success,err_msg=None):
            fut.set_result((success,err_msg))
        to_user:User = await users_repo.get_user_by_user_id(user_id=record.msg_to)
        if not to_user:
            return BaseResponse(
                message="用户id:{0} 不存在".format(record.msg_to),
                status_code=status.HTTP_400_BAD_REQUEST,
                code=-1
            )            
        await sio.emit(
            FrameType.MESSAGE.value,
            data=Message(
                type=FrameType.MESSAGE.value,
                data=AddFriendPayLoad(
                    friend_info=UserSchema.from_orm(
                        to_user
                    ),
                    user_id=user.id
                )
            ).json(),
            namespace="/im",
            callback=callback
        )
        await fut
        suc,err_msg = fut.result()
        if not suc:
            return BaseResponse(
                message="请求好友失败:{err_msg}".format(err_msg=err_msg),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                code=-1
            )
        return BaseResponse(
            message="发送成功",
            status_code=status.HTTP_200_OK
        )        
    else:
        raise RuntimeError(
            "insert friend record error!"
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
