"""add is_active to pedagogy

Revision ID: 202607130002
Revises: 202607130001
Create Date: 2026-07-13
"""

from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

revision: str = "202607130002"
down_revision: str | None = "202607130001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "pedagogical_methodologies",
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False)
    )
    op.add_column(
        "pedagogical_materials",
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False)
    )
    op.add_column(
        "daily_school_records",
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("pedagogical_methodologies", "is_active")
    op.drop_column("pedagogical_materials", "is_active")
    op.drop_column("daily_school_records", "is_active")
