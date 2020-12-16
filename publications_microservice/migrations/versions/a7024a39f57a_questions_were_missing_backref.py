"""questions were missing backref

Revision ID: a7024a39f57a
Revises: 89dc2174448e
Create Date: 2020-12-16 12:18:26.900359

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7024a39f57a'
down_revision = '89dc2174448e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'publication_question',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question', sa.String(), nullable=False),
        sa.Column('reply', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('publication_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['publication_id'],
            ['publication.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('publication_question')
    # ### end Alembic commands ###
