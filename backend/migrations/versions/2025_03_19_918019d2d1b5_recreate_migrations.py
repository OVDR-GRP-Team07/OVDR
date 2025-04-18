"""Recreate migrations

Revision ID: 918019d2d1b5
Revises: 262b3969bd2b
Create Date: 2025-03-19 00:03:42.507335

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '918019d2d1b5'
down_revision = '262b3969bd2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('closet', schema=None) as batch_op:
        batch_op.alter_column('added_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.drop_constraint('closet_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['user_id'], ondelete='CASCADE')

    with op.batch_alter_table('clothing', schema=None) as batch_op:
        batch_op.alter_column('closet_users',
               existing_type=mysql.INTEGER(),
               nullable=True,
               existing_server_default=sa.text("'0'"))
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('combination', schema=None) as batch_op:
        batch_op.alter_column('outfit_path',
               existing_type=mysql.VARCHAR(length=225),
               type_=sa.String(length=255),
               existing_nullable=False)
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.drop_constraint('combination_ibfk_2', type_='foreignkey')
        batch_op.drop_constraint('combination_ibfk_3', type_='foreignkey')
        batch_op.drop_constraint('combination_ibfk_4', type_='foreignkey')
        batch_op.create_foreign_key(None, 'clothing', ['bottom_id'], ['cid'])
        batch_op.create_foreign_key(None, 'clothing', ['dress_id'], ['cid'])
        batch_op.create_foreign_key(None, 'clothing', ['top_id'], ['cid'])

    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.drop_constraint('history_ibfk_2', type_='foreignkey')
        batch_op.create_foreign_key(None, 'clothing', ['clothing_id'], ['cid'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('history_ibfk_2', 'clothing', ['clothing_id'], ['cid'], ondelete='CASCADE')
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('combination', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('combination_ibfk_4', 'clothing', ['dress_id'], ['cid'], ondelete='SET NULL')
        batch_op.create_foreign_key('combination_ibfk_3', 'clothing', ['bottom_id'], ['cid'], ondelete='SET NULL')
        batch_op.create_foreign_key('combination_ibfk_2', 'clothing', ['top_id'], ['cid'], ondelete='SET NULL')
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('outfit_path',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=225),
               existing_nullable=False)

    with op.batch_alter_table('clothing', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('closet_users',
               existing_type=mysql.INTEGER(),
               nullable=False,
               existing_server_default=sa.text("'0'"))

    with op.batch_alter_table('closet', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('closet_ibfk_1', 'user', ['user_id'], ['user_id'])
        batch_op.alter_column('added_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    # ### end Alembic commands ###
