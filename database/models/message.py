from database.base import DeclarativeBase
import sqlalchemy as sa
import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Relationship
from database.models.user import User
from database.models.group import Group

class Message(DeclarativeBase):
    """
        im消息表
    """

    __tablename__="im_message"
    
    id = sa.Column(sa.BIGINT, primary_key=True) # TODO
    msg_from = sa.Column(ForeignKey(User.id,onupdate="CASCADE", ondelete="SET NULL"))
    _from = Relationship(User,foreign_keys=[msg_from])
    msg_to = sa.Column(ForeignKey(User.id,onupdate="CASCADE", ondelete="SET NULL"))
    _to = Relationship(User,foreign_keys=[msg_to])
    group_id = sa.Column(ForeignKey(Group.id,onupdate="CASCADE", ondelete="SET NULL"))
    group = Relationship(Group,foreign_keys=[group_id])
    _to = Relationship(User,foreign_keys=[msg_to])
    msg_content = sa.Column(sa.TEXT,comment="消息内容",nullable=True)
    msg_type=sa.Column(sa.SMALLINT,comment="消息类型",default=0)
    send_time = sa.Column(sa.DateTime,comment="发送时间",default=datetime.datetime.now)
