"""user contact phone

Revision ID: 202607140005
Revises: 202607140004
Create Date: 2026-07-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "202607140005"
down_revision: str | None = "202607140004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _has_column(table_name: str, column_name: str) -> bool:
    return any(column["name"] == column_name for column in inspect(op.get_bind()).get_columns(table_name))


def upgrade() -> None:
    if not _has_column("users", "phone"):
        op.add_column("users", sa.Column("phone", sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "phone")