from fastapi import APIRouter
from fast_api_repo.base import BaseResponse
from database.models.user import User
from database.jwt import get_current_active_user
from fastapi import Depends
from database.repositories.group import GroupInfoRepository
from database.base import get_repository
from database.schema import CreateGroupRequest,GroupSchema,GetGroupInfoRequest,UserSchema,GroupInfoUpdateRequest,InviteGroupNumberRequest
from fast_api_repo.dependency import get_sio,SocketioProxy

group_router = APIRouter()

@group_router.get(
    "",
    name="group:get-group-info",
    response_model=BaseResponse
)
async def get_group_info(
    group_info_request:GetGroupInfoRequest,
    user:User=Depends(get_current_active_user),
    group_repo:GroupInfoRepository=Depends(get_repository(GroupInfoRepository))
):
    group_list = await group_repo.get_group_info(
        creator_id=user.id,
        group_id_list=group_info_request.group_id_list
    )

    return BaseResponse(
        data=[GroupSchema.from_orm(group).dict() for group in group_list]
    )

@group_router.post(
    "",
    name="group:create-group",
    response_model=BaseResponse
)
async def create_group(
    group_form:CreateGroupRequest,
    user:User=Depends(get_current_active_user),
    group_repo:GroupInfoRepository=Depends(get_repository(GroupInfoRepository)),
    sio:SocketioProxy=Depends(get_sio)
):
    group = await group_repo.create_group(
        group_name=group_form.group_name,
        creator=user,
        group_intro=group_form.group_intro,
        notification=group_form.notification,
        init_member_list=group_form.init_member_list,
        sio=sio
    )
    schema= GroupSchema.from_orm(group)

    return BaseResponse(
        data=schema.dict()
    )

@group_router.put(
    "/{group_id}",
    name="group:modify-group",
    response_model=BaseResponse
)
async def update_group(
    group_id:int,
    group_info_update_request:GroupInfoUpdateRequest,
    user:User=Depends(get_current_active_user),
    group_repo:GroupInfoRepository=Depends(get_repository(GroupInfoRepository)),
    sio:SocketioProxy=Depends(get_sio)
):
    group = await group_repo.update_group_info(
        user=user,
        group_id=group_id,
        group_name=group_info_update_request.group_name,
        group_intro=group_info_update_request.group_intro,
        notification=group_info_update_request.notification,
        sio=sio
    )

    return BaseResponse(
        data=GroupSchema.from_orm(group).dict()
    )   


@group_router.delete(
    "/{group_id}",
    name="group:delete-group",
    response_model=BaseResponse
)
async def delete_group(
    group_id:int,
    user:User=Depends(get_current_active_user),
    group_repo:GroupInfoRepository=Depends(get_repository(GroupInfoRepository)),
    sio:SocketioProxy=Depends(get_sio)
):
    await group_repo.del_group(
        group_id=group_id,
        user=user,
        sio=sio
    )
    return BaseResponse(
        message="删除成功"
    )


@group_router.get(
    "/{group_id}/members",
    name="group:query-group-members-info",
    response_model=BaseResponse
)
async def query_group_members(
    group_id:int,
    _:User=Depends(get_current_active_user),
    group_repo:GroupInfoRepository=Depends(get_repository(GroupInfoRepository)),

):
    group_members = await group_repo.get_group_member_info(group_id=group_id)   
    data = [UserSchema.from_orm(member.user) for member in group_members]
    return BaseResponse(
        data=data
    )


@group_router.post(
    "/{group_id}/members",
    name="group:invite-group-member",
    response_model=BaseResponse
)
async def invite_group_member(
    group_id:int,
    invite_request_form:InviteGroupNumberRequest,
    user:User=Depends(get_current_active_user),
    group_repo:GroupInfoRepository=Depends(get_repository(GroupInfoRepository)),   
    sio:SocketioProxy=Depends(get_sio)
):
    await group_repo.invite_new_member(
        group_id=group_id,
        user=user,
        sio=sio,
        new_group_numbers=invite_request_form.invite_user_list
    )
    ## TODO 邀请需要验证？
    return BaseResponse(
        message="邀请成功"
    )

