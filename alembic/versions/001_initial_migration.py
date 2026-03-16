
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial_migration'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table('users',
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    op.create_table('categories',
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('desc', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('name')
    )

    op.create_table('posts',
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('caption', sa.Text(), nullable=True),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.uuid'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )

    op.create_table('media',
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('post_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('caption', sa.String(), nullable=True),
    sa.Column('media_type', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )

    op.create_table('comments',
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('post_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.uuid'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )

    op.create_table('subscriptions',
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('follower_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['follower_id'], ['users.uuid'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['target_id'], ['users.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )

    op.create_table('refresh_tokens',
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('token')
    )



def downgrade() -> None:
    op.drop_table('refresh_tokens')
    op.drop_table('subscriptions')
    op.drop_table('comments')
    op.drop_table('media')
    op.drop_table('posts')
    op.drop_table('categories')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')

