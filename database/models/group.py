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
    notification = sa.Column(sa.TEXT,nullable=True,comment="群公告")
    notification_update_time = sa.Column(sa.DateTime,nullable=True,comment="群公告时间")
    notification_user_id=sa.Column(ForeignKey(User.id,onupdate="CASCADE", ondelete="CASCADE"),comment="群公告更新人",nullable=True)
    group_intro = sa.Column(sa.Text,comment="群介绍",nullable=True)
    status = sa.Column(sa.SMALLINT,comment="群状态:0正常 1解散",default=0)
    max_member_count = sa.Column(sa.SMALLINT,comment="最大成员数",default=50)
    member_count = sa.Column(sa.SMALLINT,comment="群成员人数",default=0,nullable=False)


class GroupMemberShip(DeclarativeBase):
    """
        群成员列表
    """
    __tablename__="im_group_member_ship"

    id = sa.Column(sa.BIGINT, primary_key=True) 
    user_id = sa.Column(ForeignKey(User.id),comment="用户ID")
    user = Relationship(User,foreign_keys=[user_id])
    group_id = sa.Column(ForeignKey(Group.id),comment="群ID")
    group= Relationship(Group,foreign_keys=[group_id])
    current_contact_time=sa.Column(sa.DateTime,default=datetime.datetime.now,comment="最近更新时间")
    group_nickname=sa.Column(sa.String(256),nullable=True,comment="群昵称")
    invited_user_id=sa.Column(ForeignKey(User.id),comment="邀请的用户ID")
    role = sa.Column(sa.SMALLINT,comment="群角色 0:普通 1:管理员",default=0)
    join_time = sa.Column(sa.DateTime,comment="入群时间")
