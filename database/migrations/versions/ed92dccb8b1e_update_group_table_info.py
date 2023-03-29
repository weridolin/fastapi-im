"""update group table info 

Revision ID: ed92dccb8b1e
Revises: 62f930f9d3e1
Create Date: 2023-03-28 10:06:03.747652

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ed92dccb8b1e'
down_revision = '62f930f9d3e1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('im_group_member_ship',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('user_id', sa.BIGINT(), nullable=True, comment='用户ID'),
    sa.Column('group_id', sa.BIGINT(), nullable=True, comment='群ID'),
    sa.Column('current_contact_time', sa.DateTime(), nullable=True, comment='最近更新时间'),
    sa.Column('group_nickname', sa.String(length=256), nullable=False, comment='群昵称'),
    sa.Column('invited_user_id', sa.BIGINT(), nullable=True, comment='邀请的用户ID'),
    sa.Column('role', sa.SMALLINT(), nullable=True, comment='群角色.0:普通 1:管理员'),
    sa.Column('join_time', sa.DateTime(), nullable=True, comment='入群时间'),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('last_update', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['im_group.id'], ),
    sa.ForeignKeyConstraint(['invited_user_id'], ['im_user.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['im_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('im_user_group_ship')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('im_user_group_ship',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BIGINT(), autoincrement=False, nullable=True, comment='用户ID'),
    sa.Column('group_id', sa.BIGINT(), autoincrement=False, nullable=True, comment='群ID'),
    sa.Column('current_contact_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True, comment='最近更新时间'),
    sa.Column('group_nickname', sa.VARCHAR(length=256), autoincrement=False, nullable=False, comment='群昵称'),
    sa.Column('created', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('last_update', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('invited_user_id', sa.BIGINT(), autoincrement=False, nullable=True, comment='邀请的用户ID'),
    sa.Column('role', sa.SMALLINT(), autoincrement=False, nullable=True, comment='群角色.0:普通 1:管理员'),
    sa.Column('join_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True, comment='入群时间'),
    sa.ForeignKeyConstraint(['group_id'], ['im_group.id'], name='im_user_group_ship_group_id_fkey'),
    sa.ForeignKeyConstraint(['invited_user_id'], ['im_user.id'], name='im_user_group_ship_invited_user_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['im_user.id'], name='im_user_group_ship_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='im_user_group_ship_pkey')
    )
    op.drop_table('im_group_member_ship')
    # ### end Alembic commands ###
