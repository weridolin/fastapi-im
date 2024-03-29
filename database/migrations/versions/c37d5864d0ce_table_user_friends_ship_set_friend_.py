"""table user friends ship set [friend_nickname] nullable is true

Revision ID: c37d5864d0ce
Revises: 42dc03af605b
Create Date: 2023-03-24 14:23:01.964300

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c37d5864d0ce'
down_revision = '42dc03af605b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('im_user_friends_ship', 'friend_nickname',
               existing_type=sa.VARCHAR(length=256),
               nullable=True,
               existing_comment='好友昵称')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('im_user_friends_ship', 'friend_nickname',
               existing_type=sa.VARCHAR(length=256),
               nullable=False,
               existing_comment='好友昵称')
    # ### end Alembic commands ###
