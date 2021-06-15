"""create database game table

Revision ID: 7733e154f263
Revises: cd39376ce37d
Create Date: 2021-06-11 04:57:51.706246

"""
from alembic import op
import sqlalchemy as sa


revision = '7733e154f263'
down_revision = 'cd39376ce37d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chess_db_games",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("chess_db_id", sa.Integer, sa.ForeignKey("chess_db.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("auth0_users.id"), nullable=False),
        sa.Column("white", sa.String, nullable=False, default="New Game"),
        sa.Column("black", sa.String),
        sa.Column("event", sa.String),
        sa.Column("date", sa.Date),
        sa.Column("result", sa.String, nullable=False, default="*")
    )


def downgrade() -> None:
    op.drop_table("chess_db_games")
