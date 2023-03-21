from database.base import BaseRepository
from database.schema import UserSchema
from database.models.user import User,UserFriendShip
from typing import List
from sqlalchemy import select


class FriendShipRepository(BaseRepository):

    async def get_friends(self,user_id:int) -> List[UserFriendShip]:
        result = await self.connection.execute(select(UserFriendShip).where(UserFriendShip.user_id==user_id))
        return result.all()
        
