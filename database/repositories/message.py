from database.base import BaseRepository
from messages.schema import MessagePayLoad
from database.models.message import Message
import datetime
import pytz
from sqlalchemy import select

class MessageRepository(BaseRepository):

    async def create_message(self,message:MessagePayLoad):
        msg = Message(
            msg_from=message.msg_from,
            msg_to=message.msg_to,
            msg_content=message.msg_content,
            group_id=message.group_id,
            send_time=datetime.datetime.fromtimestamp(
                message.send_time
            )# TODO timezone
        )
        self.connection.add(msg)
        await self.connection.commit()
        return msg
    
    async def query_message(self,msg_from:int,msg_to:int,page:int,limit:int):
        res = await self.connection.execute(
            select(Message).where(
                Message.msg_from==msg_from,
                Message.msg_to==msg_to
            ).offset((page-1)*limit)
            .limit(limit)
        )
        return res.scalars().all()
        