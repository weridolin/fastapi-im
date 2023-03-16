from database.base import BaseRepository
from database.schema import UserSchema
from database.models.user import User
from database.exceptions import UserDoesNotExist
from sqlalchemy import select
class UserRepository(BaseRepository):

    async def get_user_by_email(self, *, email: str) -> UserSchema:
        user_row = await self.connection.scalars(select(User).where(User.email==email)).first()
        return user_row

    async def get_user_by_username(self, *, username: str) -> UserSchema:
        user_row = await self.connection.scalars(select(User).where(User.username==username)).first()
        return user_row
