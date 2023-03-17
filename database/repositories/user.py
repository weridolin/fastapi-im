from database.base import BaseRepository
from database.schema import UserSchema
from database.models.user import User
from database.exceptions import UserDoesNotExist
from sqlalchemy import select
class UserRepository(BaseRepository):

    async def get_user_by_email(self, *, email: str) -> UserSchema:
        result = await self.connection.execute(select(User).where(User.email==email))
        return result.scalar()

    async def get_user_by_username(self, *, username: str) -> UserSchema:
        result = await self.connection.execute(select(User).where(User.username==username))
        return result.scalar()
