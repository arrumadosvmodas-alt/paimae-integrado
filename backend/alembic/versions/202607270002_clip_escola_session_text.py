"""clip escola session cookie as text

Revision ID: 202607270002
Revises: 202607270001
Create Date: 2026-07-27
"""
from alembic import op
import sqlalchemy as sa

revision = "202607270002"
down_revision = "202607270001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "clip_escola_accounts",
        "session_cookie_encrypted",
        existing_type=sa.String(length=2000),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "clip_escola_accounts",
        "session_cookie_encrypted",
        existing_type=sa.Text(),
        type_=sa.String(length=2000),
        existing_nullable=True,
    )
