"""update group table info 

Revision ID: bc266557985c
Revises: ed92dccb8b1e
Create Date: 2023-03-28 11:45:53.091505

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc266557985c'
down_revision = 'ed92dccb8b1e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('im_group_member_ship', 'group_nickname',
               existing_type=sa.VARCHAR(length=256),
               nullable=True,
               existing_comment='群昵称')
    op.alter_column('im_group_member_ship', 'role',
               existing_type=sa.SMALLINT(),
               comment='群角色 0:普通 1:管理员',
               existing_comment='群角色.0:普通 1:管理员',
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('im_group_member_ship', 'role',
               existing_type=sa.SMALLINT(),
               comment='群角色.0:普通 1:管理员',
               existing_comment='群角色 0:普通 1:管理员',
               existing_nullable=True)
    op.alter_column('im_group_member_ship', 'group_nickname',
               existing_type=sa.VARCHAR(length=256),
               nullable=False,
               existing_comment='群昵称')
    # ### end Alembic commands ###