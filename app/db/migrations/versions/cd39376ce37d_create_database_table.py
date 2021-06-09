"""create database table

Revision ID: cd39376ce37d
Revises: 58fced675d71
Create Date: 2021-06-08 15:54:50.112067

"""
from alembic import op
import sqlalchemy as sa


revision = 'cd39376ce37d'
down_revision = '58fced675d71'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chess_db",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("auth0_users.id"), nullable=False)
    )


def downgrade() -> None:
    op.drop_table("chess_db")
