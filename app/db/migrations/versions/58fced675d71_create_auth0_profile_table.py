"""create auth0 profile table

Revision ID: 58fced675d71
Revises: 7cd9314e48bf
Create Date: 2021-05-23 11:22:51.576784

"""
from alembic import op
import sqlalchemy as sa


revision = '58fced675d71'
down_revision = '7cd9314e48bf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth0_users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("sub", sa.String, unique=True, nullable=False, index=True)
    )


def downgrade() -> None:
    op.drop_table("auth0_users")
