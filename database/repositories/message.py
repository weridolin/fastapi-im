from database.base import BaseRepository
from messages.schema import MessagePayLoad
from database.models.message import Message


class MessageRepository(BaseRepository):

    async def create_message(self,message:MessagePayLoad):
        msg = Message(
            **message.dict()
        )
        self.connection.add(msg)
        await self.connection.commit()
        return msg
    
    