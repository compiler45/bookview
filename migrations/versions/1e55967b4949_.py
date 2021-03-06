"""empty message

Revision ID: 1e55967b4949
Revises: 
Create Date: 2018-06-20 23:58:56.681386

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e55967b4949'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('articles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('book_title', sa.String(), nullable=False),
    sa.Column('book_author', sa.String(), nullable=False),
    sa.Column('time_published', sa.DateTime(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('body_text', sa.Text(), nullable=True),
    sa.Column('body_html', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('book_title')
    )
    op.create_table('articles_tags',
    sa.Column('tags_id', sa.Integer(), nullable=False),
    sa.Column('articles_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['articles_id'], ['articles.id'], ),
    sa.ForeignKeyConstraint(['tags_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('tags_id', 'articles_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('articles_tags')
    op.drop_table('articles')
    op.drop_table('tags')
    # ### end Alembic commands ###
