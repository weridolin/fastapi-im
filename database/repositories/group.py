from database.base import BaseRepository
from database.models.group import Group,GroupMemberShip
import datetime
from typing import Optional,List
from sqlalchemy import select,insert,func
from sqlalchemy.orm import selectinload
from fast_api_repo.dependency import SocketioProxy
from messages.schema import GroupInfoChangePayload,Message,GroupCreatePayload,GroupSchema,GroupDeletePayload,GroupInviteNumbersPayload
from asyncio import Future
from database.models.user import User
from database.schema import UserSchema
from database.exceptions import NoPermissionError,GroupNotFoundError
from fastapi import status

class GroupInfoRepository(BaseRepository):
    
    async def get_group_info(self,creator_id:int,group_id_list:List[int]) -> List[Group]:
        res = await self.connection.execute(
            select(Group).where(
                Group.id.in_(group_id_list),
                Group.creator_id==creator_id
            )
        )
        return res.scalars().all()

    async def create_group(self,group_name:str,creator:User,group_intro=None,notification=None,init_member_list:list=None,sio=None)-> Group:

        group = Group(
            group_name=group_name,
            creator_id=creator.id,
            owner_id=creator.id,
            notification=notification,
            notification_update_time=datetime.datetime.now(),
            notification_user_id=creator.id,
            group_intro= group_intro,
            member_count=len(init_member_list)+1
        )

        async with self.connection.begin_nested():
            self.connection.add(group)
            await self.connection.flush()
            ## 添加创建者
            params=[
                {   
                    "user_id":creator.id,
                    "group_id":group.id,
                    "invited_user_id":creator.id,
                    "join_time":datetime.datetime.now(),
                    "role":1
                }
            ]
            ## 添加初始的群成员联系表
            params.extend([
                {
                    "user_id":member_id,
                    "group_id":group.id,
                    "invited_user_id":creator.id,
                    "join_time":datetime.datetime.now()
                } for member_id in init_member_list])
            await self.connection.execute(insert(GroupMemberShip),params)

            ## 把新建群的消息推送到 初始化人员 的心想里面
            if sio:
                msg = Message(
                    data=GroupCreatePayload(
                        user=UserSchema.from_orm(creator),
                        group=GroupSchema.from_orm(group),
                        init_member_list=init_member_list
                    )
                )
                ## check message is push to socketio
                fut:Future = Future()
                async def callback(success,err_msg=None):
                    fut.set_result((success,err_msg))
                await sio.emit(
                    "message",
                    data=msg.json(),
                    namespace="/im",
                    callback=callback
                )
                await fut
            await self.connection.commit()
        return group

    async def update_group_info(self,group_id:int,user:User,group_name:str,group_intro=None,notification=None,sio:SocketioProxy=None):
        ## 更新群消息.这里 入库-->推送到推送系统 是一个完整的操作
        async with self.connection.begin_nested():
            result = await self.connection.execute(
                select(Group).where(Group.id==group_id)
            )
            group = result.scalar()
            if not group:
                raise #TODO
            group.group_intro = group_intro or group.group_intro
            group.group_name = group_name or group.group_name
            if notification:
                group.notification = notification
                group.notification_user_id = user.id 
                group.notification_update_time = datetime.datetime.now()
            if sio:
                ## 推送消息到推送系统
                result = await self.connection.execute(
                    select(GroupMemberShip).where(GroupMemberShip.group_id==group_id)
                )

                group_member_list = [member.user_id for member in result.scalars().all()]
                msg = Message(
                    data=GroupInfoChangePayload(
                        user=UserSchema.from_orm(user),
                        group_name=group_name,
                        group_intro=group_intro,
                        notification=notification,
                        group_id=group_id,
                        group_number_list=group_member_list,
                    )
                )
                ## check message is push to socketio
                fut:Future = Future()
                async def callback(success,err_msg=None):
                    fut.set_result((success,err_msg))
                await sio.emit(
                    "message",
                    data=msg.json(),
                    namespace="/im",
                    callback=callback
                )
                await fut
            await self.connection.commit()
            return group

    async def del_group(self,group_id:int,user:User,sio:SocketioProxy=None):
        async with self.connection.begin_nested():
            result = await self.connection.execute(
                select(Group).where(Group.id==group_id)
            )
            group = result.scalar()
            if group.owner_id!=user.id:
                raise NoPermissionError(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="当前用户没有删除的权限."
                )
            ## 状态位标记为解散
            group.status=1

            ## 获取群成员列表
            group_members = await self.connection.execute(
                select(GroupMemberShip).where(
                    GroupMemberShip.group_id==group_id
                )
            )
            group_member_list = [member.user_id for member in group_members.scalars().all() if member.user_id!=user.id]

            ## 推送解散消息到所有群成员的消息信箱
            msg = Message(
                data=GroupDeletePayload(
                    user=UserSchema.from_orm(user),
                    group=GroupSchema.from_orm(group),
                    group_number_list=group_member_list
                )
            )
            print(msg,">>>>")
            ## check message is push to socketio
            fut:Future = Future()
            async def callback(success,err_msg=None):
                fut.set_result((success,err_msg))
            await sio.emit(
                "message",
                data=msg.json(),
                namespace="/im",
                callback=callback
            )
            await fut
            return await self.connection.commit()

    async def get_group_member_count(self,group_id:int) -> int:
        result = await self.connection.execute(
                select(func.count(GroupMemberShip.id)).where(
                    GroupMemberShip.group_id==group_id
                )    
        )
        res = result.scalar()
        return res

    async def get_group_member_info(self,group_id:int):
        result = await self.connection.execute(
            select(GroupMemberShip).where(
                GroupMemberShip.group_id==group_id
            ).options(
                selectinload(GroupMemberShip.user)
            )
        )

        return result.scalars().all()
    
    async def invite_new_member(self,group_id:int,user:User,new_group_numbers:List[int],sio:SocketioProxy=None): 
        async with self.connection.begin_nested():
            result = await self.connection.execute(
                select(Group).where(Group.id==group_id)
            )
            group = result.scalar_one()
            if not group:
                raise GroupNotFoundError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"can not find group by id:{group_id}"
                )
            group.member_count+=len(new_group_numbers)
            ## 新的群成员信息
            params=[
                {   
                    "user_id":member,
                    "group_id":group_id,
                    "invited_user_id":user.id,
                    "join_time":datetime.datetime.now(),
                    "role":0
                } for member in new_group_numbers
            ]
            await self.connection.execute(insert(GroupMemberShip),params)

            if sio:
                ## check message is push to socketio
                msg = Message(
                    data=GroupInviteNumbersPayload(
                        user=UserSchema.from_orm(user),
                        new_number_list=new_group_numbers,
                        group=GroupSchema.from_orm(group)
                    )
                )
                fut:Future = Future()
                async def callback(success,err_msg=None):
                    fut.set_result((success,err_msg))
                await sio.emit(
                    "message",
                    data=msg.json(),
                    namespace="/im",
                    callback=callback
                )
                await fut
            return await self.connection.commit()