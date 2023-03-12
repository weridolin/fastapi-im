import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Relationship
import datetime

DB_URL = "sqlite:///im.db"
import datetime

class Base(object):

    created = sa.Column(
        sa.DateTime(timezone=True),
        default=datetime.datetime.now,
        nullable=False
    )
    last_update = sa.Column(
        sa.DateTime(timezone=True),
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        nullable=False
    )

class User(Base):
    """
        用户信息表
    """
    __tablename__="im_user"

    SEX_CHOICE=(
    )
    
    id = sa.Column(sa.BIGINT, primary_key=True) # TODO   
    username = sa.Column(sa.String(256),unique=True,comment="用户名",nullable=False)
    password = sa.Column(sa.String(256),comment="用户账号密码",nullable=False)
    email = sa.Column(sa.String(256),comment="账号邮箱",unique=True,nullable=False)
    telephone = sa.Column(sa.String(256),comment="用户电话",nullable=True)
    avatar = sa.Column(sa.String(256),comment="用户头像",nullable=True)
    age = sa.Column(sa.SMALLINT,comment="用户年龄",nullable=True)
    sex = sa.Column(sa.SMALLINT,comment="用户性别",nullable=True)

class UserFriendShip(Base):
    """
        用户好友列表
    """
    __tablename__="im_user_friends_ship"

    id = sa.Column(sa.BIGINT, primary_key=True) 
    user_id = sa.Column(ForeignKey(User.id),comment="用户ID")
    user = Relationship(User,foreign_keys=[user_id])
    friend_id = sa.Column(ForeignKey(User.id),comment="好友ID")
    friend_group=sa.Column(sa.String(256),nullable=True,default="我的好友")
    current_contact_time=sa.Column(sa.DATETIME,default=datetime.datetime.now,comment="最近联系时间")
    friend_nickname=sa.Column(sa.String(256),nullable=False,comment="好友昵称")
    relationship=sa.Column(sa.SMALLINT,comment="好友关系(1:好友 2:陌生人)",nullable=False,default=1)

class UserGroupShip(Base):
    """
        用户群列表
    """
    __tablename__="im_user_friends_ship"

    id = sa.Column(sa.BIGINT, primary_key=True) 
    user_id = sa.Column(ForeignKey(User.id),comment="用户ID")
    user = Relationship(User,foreign_keys=[user_id])
    group_id = sa.Column(ForeignKey(User.id),comment="群ID")
    group= Relationship("Group",foreign_keys=[group_id])
    current_contact_time=sa.Column(sa.DATETIME,default=datetime.datetime.now,comment="最近更新时间")
    group_nickname=sa.Column(sa.String(256),nullable=False,comment="群昵称")


class Group(Base):
    """
        群信息表
    """

    __tablename__="im_group"

    id = sa.Column(sa.BIGINT, primary_key=True) #
    group_name = sa.Column(sa.String(256),comment="群聊名称",nullable=False)
    creator_id = sa.Column(ForeignKey(User.id,onupdate="CASCADE", ondelete="SCASCADE"),comment="创建者") 
    creator = Relationship(User,foreign_keys=[creator_id])
    created_time = sa.Column(sa.DateTime,default=datetime.datetime.now)
    owner_id =  sa.Column(ForeignKey(User.id,onupdate="CASCADE", ondelete="SCASCADE"),comment="群主") 
    announcement = sa.Column(sa.TEXT,nullable=True,comment="群公告")

class GroupUserShip(Base):
    """
        群成员表
    """
    id = sa.Column(sa.BIGINT, primary_key=True) #
    group_id = sa.Column(ForeignKey(Group.id,onupdate="CASCADE", ondelete="SCASCADE"),comment="群id")
    user_id = sa.Column(ForeignKey(User.id,onupdate="CASCADE", ondelete="SCASCADE"),comment="用户ID")
    group = Relationship(Group,foreign_keys=[group_id])
    user=Relationship(User,foreign_keys=[user_id])
    group_nickname=sa.Column(sa.String(256),nullable=False,comment="群昵称")


class Message(Base):
    """
        im消息表
    """

    __tablename__="im_message"
    
    id = sa.Column(sa.BIGINT, primary_key=True) # TODO
    msg_from = sa.Column(ForeignKey(User.id,onupdate="CASCADE", ondelete="SET NULL"))
    _from = Relationship(User,foreign_keys=[msg_from])
    msg_to = sa.Column(ForeignKey(User.id,onupdate="CASCADE", ondelete="SET NULL"))
    _to = Relationship(User,foreign_keys=[msg_to])
    msg_content = sa.Column(sa.TEXT,comment="消息内容",nullable=True)
    msg_type=sa.Column(sa.SMALLINT,comment="消息类型",default=0)
    send_time = sa.Column(sa.DATETIME,comment="发送时间",default=datetime.datetime.now)


DeclarativeBase = declarative_base(cls=Base)



from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DB_URL, 
    connect_args={"check_same_thread": False}
)
DeclarativeBase.metadata.create_all(engine)

from sqlalchemy.ext.asyncio import  AsyncSession,async_sessionmaker
from sqlalchemy.ext.asyncio.scoping import async_scoped_session
from asyncio import current_task


async_session = async_scoped_session(
    async_sessionmaker(
        engine,
        class_=AsyncSession,
    ),
    scopefunc=current_task,
)