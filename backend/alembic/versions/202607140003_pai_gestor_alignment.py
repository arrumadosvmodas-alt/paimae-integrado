"""pai gestor alignment

Revision ID: 202607140003
Revises: 202607140002
Create Date: 2026-07-14
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "202607140003"
down_revision = "202607140002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "guardian_profiles",
        sa.Column("guardian_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("preferred_channel", sa.String(length=20), nullable=False, server_default="app"),
        sa.Column("daily_summary_time", sa.String(length=5), nullable=True),
        sa.Column("evening_activity_time", sa.String(length=5), nullable=True),
        sa.Column("notification_preferences", sa.JSON(), nullable=True),
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["guardian_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("guardian_id"),
    )
    op.create_index(op.f("ix_guardian_profiles_guardian_id"), "guardian_profiles", ["guardian_id"], unique=True)

    op.create_table(
        "material_index_entries",
        sa.Column("material_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_type", sa.String(length=20), nullable=False, server_default="book"),
        sa.Column("chapter", sa.String(length=80), nullable=True),
        sa.Column("page_start", sa.Integer(), nullable=True),
        sa.Column("page_end", sa.Integer(), nullable=True),
        sa.Column("theme", sa.String(length=180), nullable=False),
        sa.Column("skills", sa.JSON(), nullable=True),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("review_status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["material_id"], ["pedagogical_materials.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_material_index_entries_material_id"), "material_index_entries", ["material_id"], unique=False)

    op.create_table(
        "school_schedules",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("subject", sa.String(length=80), nullable=False),
        sa.Column("topic", sa.String(length=180), nullable=True),
        sa.Column("source", sa.String(length=20), nullable=False, server_default="manual"),
        sa.Column("source_file_url", sa.String(length=500), nullable=True),
        sa.Column("confidence_score", sa.Integer(), nullable=True),
        sa.Column("fallback_used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="planned"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_school_schedules_child_id"), "school_schedules", ["child_id"], unique=False)
    op.create_index(op.f("ix_school_schedules_date"), "school_schedules", ["date"], unique=False)
    op.create_index(op.f("ix_school_schedules_school_id"), "school_schedules", ["school_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_school_schedules_school_id"), table_name="school_schedules")
    op.drop_index(op.f("ix_school_schedules_date"), table_name="school_schedules")
    op.drop_index(op.f("ix_school_schedules_child_id"), table_name="school_schedules")
    op.drop_table("school_schedules")
    op.drop_index(op.f("ix_material_index_entries_material_id"), table_name="material_index_entries")
    op.drop_table("material_index_entries")
    op.drop_index(op.f("ix_guardian_profiles_guardian_id"), table_name="guardian_profiles")
    op.drop_table("guardian_profiles")