from database.base import BaseRepository
from database.models.user import User
from database.exceptions import UserDoesNotExist
from sqlalchemy import select,delete
from fast_api_repo.auth.encrypt import encrypt_by_md5
from settings import AppSettings
from fast_api_repo.auth.schema import JWTPayLoad
import jwt
from typing import Optional,List
from database.models.user import UserFriendShip
from sqlalchemy.orm import selectinload
from sqlalchemy import or_

class UserRepository(BaseRepository):

    async def get_user_by_email(self, *, email: str) -> Optional[User]:
        result = await self.connection.execute(select(User).where(User.email==email))
        return result.scalar()

    async def get_user_by_username(self, *, username: str) -> Optional[User]:
        result = await self.connection.execute(select(User).where(User.username==username))
        return result.scalar()

    async def get_user_by_user_id(self, *, user_id: int) -> Optional[User]:
        result = await self.connection.execute(select(User).where(User.id==user_id))
        return result.scalar()

    async def create_user(self,username:str,password:str,email:str,salt:str):
        password = encrypt_by_md5(password,salt)
        user = User(
            username=username,
            password=password,
            email=email
        )
        self.connection.add(user)
        await self.connection.commit()
        return user
    

    async def get_friends(self,user_id:int):
        result = await self.connection.execute(
            select(UserFriendShip).
            where(UserFriendShip.user_id==user_id).
            order_by(UserFriendShip.current_contact_time).
            options(
                selectinload(UserFriendShip.friend)
            )
        )
        return result.scalars().all()

    async def del_friend(self,user_id:int,del_friend_id:int):
        await self.connection.execute(
            delete(UserFriendShip).
            where(UserFriendShip.user_id==user_id,UserFriendShip.friend_id==del_friend_id)
        )
        return await self.connection.commit()


    async def search(self,keyword:str,page:int,limit:int):
        res = await self.connection.execute(
            select(User).where(
                or_(
                    User.username.ilike(f"%{keyword}%"),
                    User.telephone.ilike(f"%{keyword}%"),
                )
            ).offset((page-1)*limit)
            .limit(limit)
        )
        return res.scalars().all()