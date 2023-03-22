from database.base import BaseRepository
from database.schema import UserSchema
from database.models.user import User,UserFriendShip
from database.models.friends import FriendManagerRecord
from typing import List
from sqlalchemy import select


class FriendShipRepository(BaseRepository):

    async def get_friends(self,user_id:int) -> List[UserFriendShip]:
        result=await self.connection.execute(select(UserFriendShip).where(UserFriendShip.user_id==user_id))
        return result.all()
        
    async def add_friend(self,request_user_id:int,friend_user_id:int):
        record = FriendManagerRecord(
                msg_from=request_user_id,
                msg_to=friend_user_id
            )
        self.connection.add(record)
        await self.connection.commit()
    