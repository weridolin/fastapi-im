from database.base import DeclarativeBase
import sqlalchemy as sa
import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Relationship
from sqlalchemy import UniqueConstraint

class User(DeclarativeBase):
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


class UserFriendShip(DeclarativeBase):
    """
        用户好友列表
    """
    __tablename__="im_user_friends_ship"
    __table_args__ = (
        UniqueConstraint("user_id","friend_id"),
    )

    id = sa.Column(sa.BIGINT, primary_key=True) 
    user_id = sa.Column(ForeignKey(User.id),comment="用户ID")
    user = Relationship(User,foreign_keys=[user_id])
    friend_id = sa.Column(ForeignKey(User.id),comment="好友ID")
    friend = Relationship(User,foreign_keys=[friend_id])
    friend_group=sa.Column(sa.String(256),nullable=True,default="我的好友")
    current_contact_time=sa.Column(sa.DateTime,default=datetime.datetime.now,comment="最近联系时间")
    friend_nickname=sa.Column(sa.String(256),nullable=True,comment="好友昵称")
    relationship=sa.Column(sa.SMALLINT,comment="好友关系(1:好友 2:陌生人)",nullable=False,default=1)

