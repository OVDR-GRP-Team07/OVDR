"""Recreate migrations

Revision ID: a84386ef1853
Revises: e0db236f1a2a
Create Date: 2025-03-19 02:47:00.447015

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a84386ef1853'
down_revision = 'e0db236f1a2a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('combination', schema=None) as batch_op:
        batch_op.drop_constraint('combination_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['user_id'], ondelete='CASCADE')

    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.drop_constraint('history_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['user_id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('history_ibfk_1', 'user', ['user_id'], ['user_id'])

    with op.batch_alter_table('combination', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('combination_ibfk_1', 'user', ['user_id'], ['user_id'])

    # ### end Alembic commands ###
