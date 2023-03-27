from fastapi import APIRouter
from fast_api_repo.base import BaseErrResponse,BaseResponse
from database.models.user import User
from database.jwt import get_current_active_user
from database.repositories.friends import FriendShipRepository
from database.base import get_repository
from fastapi import Depends
from database.repositories.user import UserRepository
from database.repositories.message import MessageRepository
from fast_api_repo.message.schema import GetMessageHistoryRequest,MessagePayLoad
from fast_api_repo.dependency import paginate_params


msg_router = APIRouter()

@msg_router.get(
    "/history",
    name="messages:history",
    response_model=BaseResponse
)
async def get_message(
    query_request_form:GetMessageHistoryRequest,
    user:User=Depends(get_current_active_user),
    msg_repo:MessageRepository= Depends(get_repository(MessageRepository)),
    paginate_params:dict = Depends(paginate_params)
):  
    print(">>>>",user.id,query_request_form.msg_to)
    res = await msg_repo.query_message(
        msg_from=user.id,
        msg_to=query_request_form.msg_to,
        page=paginate_params["page"],
        limit=paginate_params["limit"]
    )
    data = [MessagePayLoad.from_orm(msg).dict() for msg in res]
    return BaseResponse(
        data=data
    )