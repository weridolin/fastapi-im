from database.base import DeclarativeBase
import sqlalchemy as sa
import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Relationship
from database.models.user import User

class Group(DeclarativeBase):
    """
        群信息表
    """

    __tablename__="im_group"

    id = sa.Column(sa.BIGINT, primary_key=True) #
    group_name = sa.Column(sa.String(256),comment="群聊名称",nullable=False)
    creator_id = sa.Column(ForeignKey(User.id,onupdate="CASCADE", ondelete="CASCADE"),comment="创建者") 
    creator = Relationship(User,foreign_keys=[creator_id])
    created_time = sa.Column(sa.DateTime,default=datetime.datetime.now)
    owner_id =  sa.Column(ForeignKey(User.id,onupdate="CASCADE", ondelete="CASCADE"),comment="群主") 
    announcement = sa.Column(sa.TEXT,nullable=True,comment="群公告")