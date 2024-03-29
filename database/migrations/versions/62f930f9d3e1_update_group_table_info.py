"""update group table info 

Revision ID: 62f930f9d3e1
Revises: 4b4b59f3d83a
Create Date: 2023-03-28 10:02:41.061107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62f930f9d3e1'
down_revision = '4b4b59f3d83a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('im_group', sa.Column('notification', sa.TEXT(), nullable=True, comment='群公告'))
    op.add_column('im_group', sa.Column('notification_update_time', sa.DateTime(), nullable=True, comment='群公告时间'))
    op.add_column('im_group', sa.Column('notification_user_id', sa.BIGINT(), nullable=True, comment='群公告更新人'))
    op.add_column('im_group', sa.Column('group_intro', sa.Text(), nullable=True, comment='群介绍'))
    op.add_column('im_group', sa.Column('statues', sa.SMALLINT(), nullable=True, comment='群状态:0正常 1解散'))
    op.add_column('im_group', sa.Column('max_member_count', sa.SMALLINT(), nullable=True, comment='最大成员数'))
    op.create_foreign_key(None, 'im_group', 'im_user', ['notification_user_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.drop_column('im_group', 'announcement')
    op.add_column('im_user_group_ship', sa.Column('invited_user_id', sa.BIGINT(), nullable=True, comment='邀请的用户ID'))
    op.add_column('im_user_group_ship', sa.Column('role', sa.SMALLINT(), nullable=True, comment='群角色.0:普通 1:管理员'))
    op.add_column('im_user_group_ship', sa.Column('join_time', sa.DateTime(), nullable=True, comment='入群时间'))
    op.create_foreign_key(None, 'im_user_group_ship', 'im_user', ['invited_user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'im_user_group_ship', type_='foreignkey')
    op.drop_column('im_user_group_ship', 'join_time')
    op.drop_column('im_user_group_ship', 'role')
    op.drop_column('im_user_group_ship', 'invited_user_id')
    op.add_column('im_group', sa.Column('announcement', sa.TEXT(), autoincrement=False, nullable=True, comment='群公告'))
    op.drop_constraint(None, 'im_group', type_='foreignkey')
    op.drop_column('im_group', 'max_member_count')
    op.drop_column('im_group', 'statues')
    op.drop_column('im_group', 'group_intro')
    op.drop_column('im_group', 'notification_user_id')
    op.drop_column('im_group', 'notification_update_time')
    op.drop_column('im_group', 'notification')
    # ### end Alembic commands ###
