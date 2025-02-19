"""Initial migration

Revision ID: 7ca3d7a4b8af
Revises: 399ef5ecfcd5
Create Date: 2024-12-28 11:18:30.906345

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ca3d7a4b8af'
down_revision = '399ef5ecfcd5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('business', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone_number', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('social_media_links', sa.JSON(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('business', schema=None) as batch_op:
        batch_op.drop_column('social_media_links')
        batch_op.drop_column('phone_number')

    # ### end Alembic commands ###
