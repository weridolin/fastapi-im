from fastapi import APIRouter
from fast_api_repo.friends.schema import AddFriendRequest,BaseResponse,DealFriendAskRequest,SearchForm
from fastapi import  Depends
from database.jwt import get_current_active_user
from database.base import get_repository
from database.repositories.friends import FriendShipRepository
from database.repositories.user import UserRepository
from database.models.user import User
from database.schema import UserSchema
from fast_api_repo.dependency import get_sio,SocketioProxy
from messages.schema import Message,FrameType,AddFriendPayLoad,UserSchema,AcceptFriendPayLoad,RefuseFriendPayLoad
from asyncio.futures import Future
from fastapi import status
from fast_api_repo.dependency import paginate_params


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
    if await friends_manager_repo.get_friend_apply_record(
        request_user_id=user.id,
        friend_user_id=request_form.friend_user_id
    ):
        return BaseResponse(
                message="正在等待对方通过申请...",
                status_code=status.HTTP_200_OK
            )        
    else:
        record = await friends_manager_repo.add_friend(
            request_user_id=user.id,
            friend_user_id=request_form.friend_user_id,
            check_info=request_form.check_info
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
                        from_id=user.id,
                        request_id=record.id,
                        to_id=to_user.id
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


@friend_router.put(
    "",
    name="friend:accept-or-update-friend",
    response_model=BaseResponse
)
async def deal_friend(
    request_form:DealFriendAskRequest,
    user:User=Depends(get_current_active_user),
    friends_manager_repo:FriendShipRepository= Depends(get_repository(FriendShipRepository)),
    sio:SocketioProxy = Depends(get_sio),
):
    record = await friends_manager_repo.deal_friend_apply(
        record_id=request_form.request_id,
        accept=request_form.accept,
        refuse_reason=request_form.refuse_reason
    )
    fut:Future=Future()
    async def callback(success,err_msg=None):
        fut.set_result((success,err_msg))   

    ## 把通过好友验证的消息发送给申请方,如果对方在线的话
    await sio.emit(
        FrameType.MESSAGE.value,
        data=Message(
            type=FrameType.MESSAGE.value,
            data=AcceptFriendPayLoad(
                friend_info=UserSchema.from_orm(user),
                from_id=user.id,
                request_id=record.id,
                to_id=record.msg_from
            ) if request_form.accept else
            RefuseFriendPayLoad(
                friend_info=UserSchema.from_orm(user),
                from_id=user.id,
                request_id=record.id,
                to_id=record.msg_from        
            )
        ).json(),
        namespace="/im",
        callback=callback
    )
    
    await fut
    suc,err_msg = fut.result()
    if not suc:
        return BaseResponse(
            message="接受好友失败！:{err_msg}".format(err_msg=err_msg),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=-1
        )
    return BaseResponse(
        message="接受好友成功",
        status_code=status.HTTP_200_OK
    )        



@friend_router.get(
    "/search",
    name="friend:search-friend",
    response_model=BaseResponse
)
async def search(
    search_form:SearchForm,
    user:User=Depends(get_current_active_user),
    user_repo:UserRepository= Depends(get_repository(UserRepository)),  
    pagination_params:dict=Depends(paginate_params)  
):
    res = await user_repo.search(
        keyword=search_form.keyword,
        page=pagination_params["page"],
        limit=pagination_params['limit']
    )

    data = [UserSchema.from_orm(msg).dict() for msg in res]
    return BaseResponse(
        data=data
    )

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
