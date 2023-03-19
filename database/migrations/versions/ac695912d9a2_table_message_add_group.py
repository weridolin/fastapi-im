"""table 'message' add group

Revision ID: ac695912d9a2
Revises: a0f2be203e73
Create Date: 2023-03-19 20:45:33.578651

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac695912d9a2'
down_revision = 'a0f2be203e73'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('im_message', sa.Column('group_id', sa.BIGINT(), nullable=True))
    op.create_foreign_key(None, 'im_message', 'im_group', ['group_id'], ['id'], onupdate='CASCADE', ondelete='SET NULL')
    op.drop_constraint('im_user_group_ship_group_id_fkey', 'im_user_group_ship', type_='foreignkey')
    op.create_foreign_key(None, 'im_user_group_ship', 'im_group', ['group_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'im_user_group_ship', type_='foreignkey')
    op.create_foreign_key('im_user_group_ship_group_id_fkey', 'im_user_group_ship', 'im_user', ['group_id'], ['id'])
    op.drop_constraint(None, 'im_message', type_='foreignkey')
    op.drop_column('im_message', 'group_id')
    # ### end Alembic commands ###