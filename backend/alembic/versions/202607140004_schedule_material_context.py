"""schedule material context

Revision ID: 202607140004
Revises: 202607140003
Create Date: 2026-07-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision: str = "202607140004"
down_revision: str | None = "202607140003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _has_column(table_name: str, column_name: str) -> bool:
    return any(column["name"] == column_name for column in inspect(op.get_bind()).get_columns(table_name))


def _has_index(table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspect(op.get_bind()).get_indexes(table_name))


def upgrade() -> None:
    if not _has_column("school_schedules", "material_id"):
        op.add_column("school_schedules", sa.Column("material_id", postgresql.UUID(as_uuid=True), nullable=True))
    if not _has_column("school_schedules", "chapter"):
        op.add_column("school_schedules", sa.Column("chapter", sa.String(length=80), nullable=True))
    if not _has_column("school_schedules", "page_start"):
        op.add_column("school_schedules", sa.Column("page_start", sa.Integer(), nullable=True))
    if not _has_column("school_schedules", "page_end"):
        op.add_column("school_schedules", sa.Column("page_end", sa.Integer(), nullable=True))
    if not _has_index("school_schedules", op.f("ix_school_schedules_material_id")):
        op.create_index(op.f("ix_school_schedules_material_id"), "school_schedules", ["material_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_school_schedules_material_id"), table_name="school_schedules")
    op.drop_column("school_schedules", "page_end")
    op.drop_column("school_schedules", "page_start")
    op.drop_column("school_schedules", "chapter")
    op.drop_column("school_schedules", "material_id")