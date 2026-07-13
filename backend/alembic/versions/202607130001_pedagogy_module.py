"""pedagogy module

Revision ID: 202607130001
Revises: 202607110001
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202607130001"
down_revision: str | None = "202607110001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. methodologies
    op.create_table(
        "pedagogical_methodologies",
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pedagogical_methodologies_school_id"),
        "pedagogical_methodologies",
        ["school_id"],
        unique=False,
    )

    # 2. materials
    op.create_table(
        "pedagogical_materials",
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("author", sa.String(length=100), nullable=True),
        sa.Column("isbn", sa.String(length=20), nullable=True),
        sa.Column("subject", sa.String(length=80), nullable=False),
        sa.Column("pedagogical_line", sa.String(length=100), nullable=False),
        sa.Column("objectives", sa.Text(), nullable=True),
        sa.Column("family_orientation", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pedagogical_materials_school_id"),
        "pedagogical_materials",
        ["school_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pedagogical_materials_isbn"),
        "pedagogical_materials",
        ["isbn"],
        unique=False,
    )

    # 3. material items
    op.create_table(
        "material_items",
        sa.Column("material_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chapter", sa.String(length=50), nullable=True),
        sa.Column("page", sa.String(length=20), nullable=True),
        sa.Column("theme", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["material_id"], ["pedagogical_materials.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_material_items_material_id"),
        "material_items",
        ["material_id"],
        unique=False,
    )

    # 4. daily records
    op.create_table(
        "daily_school_records",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("observed_skills", sa.Text(), nullable=True),
        sa.Column("engagement_score", sa.Integer(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_daily_school_records_child_id"),
        "daily_school_records",
        ["child_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_daily_school_records_date"),
        "daily_school_records",
        ["date"],
        unique=False,
    )

    # 5. family interaction suggestions
    op.create_table(
        "family_interaction_suggestions",
        sa.Column("daily_record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("suggestion_text", sa.Text(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["daily_record_id"], ["daily_school_records.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_family_interaction_suggestions_daily_record_id"),
        "family_interaction_suggestions",
        ["daily_record_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("family_interaction_suggestions")
    op.drop_table("daily_school_records")
    op.drop_table("material_items")
    op.drop_table("pedagogical_materials")
    op.drop_table("pedagogical_methodologies")
