"""friendship add unique constraint

Revision ID: 4b4b59f3d83a
Revises: c37d5864d0ce
Create Date: 2023-03-24 16:46:49.805468

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b4b59f3d83a'
down_revision = 'c37d5864d0ce'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'im_user_friends_ship', ['user_id', 'friend_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'im_user_friends_ship', type_='unique')
    # ### end Alembic commands ###
