"""add replied at

Revision ID: aa2a6c05e129
Revises: a7024a39f57a
Create Date: 2020-12-16 12:38:56.635976

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa2a6c05e129'
down_revision = 'a7024a39f57a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'publication_question', sa.Column('replied_at', sa.DateTime(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('publication_question', 'replied_at')
    # ### end Alembic commands ###
