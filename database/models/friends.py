from database.base import DeclarativeBase
import sqlalchemy as sa
import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Relationship
from database.models.user import User


class FriendManagerRecord(DeclarativeBase):
    """
        
    """

    __tablename__="im_friend_manager_record"

    id = sa.Column(sa.BIGINT, primary_key=True) # TODO
    msg_from = sa.Column(ForeignKey(User.id,onupdate="CASCADE", ondelete="SET NULL"))
    _from = Relationship(User,foreign_keys=[msg_from])
    msg_to = sa.Column(ForeignKey(User.id,onupdate="CASCADE", ondelete="SET NULL"))
    _to = Relationship(User,foreign_keys=[msg_to])
    request_time = sa.Column(sa.DateTime,comment="发送时间",default=datetime.datetime.now)
    deal_time = sa.Column(sa.DateTime,comment="处理时间",nullable=True)
    accept = sa.Column(sa.Boolean,comment="是否通过",nullable=False,default=False)
    check_info = sa.Column(sa.TEXT,comment="验证消息描述",nullable=True)