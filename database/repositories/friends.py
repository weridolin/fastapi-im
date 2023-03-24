from database.base import BaseRepository
from database.schema import UserSchema
from database.models.user import User,UserFriendShip
from database.models.friends import FriendManagerRecord
from typing import List
from sqlalchemy import select,insert
from database.models.user import UserFriendShip
from fastapi.exceptions import HTTPException
from fastapi import status
import datetime
from sqlalchemy.exc import IntegrityError

class FriendShipRepository(BaseRepository):

    async def get_friends(self,user_id:int) -> List[UserFriendShip]:
        result=await self.connection.execute(select(UserFriendShip).where(UserFriendShip.user_id==user_id))
        return result.all()
        
    async def add_friend(self,request_user_id:int,friend_user_id:int,check_info:str) -> FriendManagerRecord:
        # record = await self.connection.execute(
        #     insert(FriendManagerRecord).values(
        #         msg_from=request_user_id,
        #         msg_to=friend_user_id
        #     ).options(
        #         selectinload(FriendManagerRecord._from)
        #     )
        # )
        # print(record.scalar())
        record = FriendManagerRecord(
                msg_from=request_user_id,
                msg_to=friend_user_id,
                check_info=check_info
            )
        self.connection.add(record)
        await self.connection.commit()
        return record
    
    async def get_friend_apply_record(self,request_user_id:int,friend_user_id:int)->FriendManagerRecord:
        record = await self.connection.execute(select(FriendManagerRecord).where(
            FriendManagerRecord.msg_to==friend_user_id,FriendManagerRecord.msg_from==request_user_id)
        )
        return record.scalar()
    
    async def deal_friend_apply(self,record_id:int,accept:bool,refuse_reason=None): ##
        self.connection.begin()
        record:FriendManagerRecord = await self.connection.execute(
            select(FriendManagerRecord).
            where(FriendManagerRecord.id==record_id))
        record=record.scalar()
        if record:
            record.accept = accept
            record.refuse_reason=refuse_reason
            record.deal_time = datetime.datetime.now()
            
            ## update friendship table
            try:
                if accept:
                    
                    await self.connection.execute(
                        insert(UserFriendShip).values(
                            user_id=record.msg_from,
                            friend_id=record.msg_to
                        )
                    )
            except IntegrityError as error:
                print(f"user:{record.msg_from} friend:{record.msg_to} is exist",type(error))
            await self.connection.commit()

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"申请记录id:{record_id}不存在！"
            )
        return record