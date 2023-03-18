from database.base import BaseRepository
from database.schema import UserSchema
from database.models.user import User
from database.exceptions import UserDoesNotExist
from sqlalchemy import select
from fast_api_repo.auth.encrypt import encrypt_by_md5
from fast_api_repo.settings import AppSettings
from fast_api_repo.auth.schema import JWTPayLoad
import jwt
from typing import Optional


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
    

