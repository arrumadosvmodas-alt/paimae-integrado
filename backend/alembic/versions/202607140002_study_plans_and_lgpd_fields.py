"""study plans, interactions, material processing fields and LGPD user fields

Revision ID: 202607140002
Revises: 202607140001
Create Date: 2026-07-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202607140002"
down_revision: str | None = "202607140001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- Campos adicionais de intake da criança ---
    op.add_column("children", sa.Column("grade", sa.String(length=20), nullable=True))
    op.add_column("children", sa.Column("shift", sa.String(length=20), nullable=True))
    op.add_column("children", sa.Column("preferences", sa.JSON(), nullable=True))
    op.add_column("children", sa.Column("difficulties", sa.JSON(), nullable=True))
    op.add_column("children", sa.Column("observations", sa.Text(), nullable=True))

    # --- Processamento de materiais (OCR/IA) ---
    op.add_column("pedagogical_materials", sa.Column("file_url", sa.String(length=500), nullable=True))
    op.add_column("pedagogical_materials", sa.Column("extracted_text", sa.Text(), nullable=True))
    op.add_column("pedagogical_materials", sa.Column("ai_analysis", sa.JSON(), nullable=True))
    op.add_column(
        "pedagogical_materials",
        sa.Column("processing_status", sa.String(length=20), server_default="pending", nullable=False),
    )
    op.add_column("pedagogical_materials", sa.Column("processing_error", sa.Text(), nullable=True))

    # --- Planos de estudo e interações ---
    op.create_table(
        "study_plans",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("material_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("ai_generated_plan", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.ForeignKeyConstraint(["material_id"], ["pedagogical_materials.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_study_plans_child_id"), "study_plans", ["child_id"], unique=False)
    op.create_index(op.f("ix_study_plans_material_id"), "study_plans", ["material_id"], unique=False)

    op.create_table(
        "daily_study_plan_items",
        sa.Column("study_plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("chapter_or_theme", sa.String(length=180), nullable=False),
        sa.Column("activity_description", sa.Text(), nullable=True),
        sa.Column("difficulty_level", sa.String(length=20), nullable=False),
        sa.Column("estimated_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["study_plan_id"], ["study_plans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_daily_study_plan_items_study_plan_id"), "daily_study_plan_items", ["study_plan_id"], unique=False)
    op.create_index(op.f("ix_daily_study_plan_items_date"), "daily_study_plan_items", ["date"], unique=False)

    # --- LGPD / primeiro acesso (usuários) ---
    op.add_column("users", sa.Column("document", sa.String(length=14), nullable=True))
    op.add_column(
        "users",
        sa.Column("first_access_completed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("lgpd_accepted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column("users", sa.Column("lgpd_accepted_at", sa.DateTime(), nullable=True))
    op.create_index(op.f("ix_users_document"), "users", ["document"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_document"), table_name="users")
    op.drop_column("users", "lgpd_accepted_at")
    op.drop_column("users", "lgpd_accepted")
    op.drop_column("users", "first_access_completed")
    op.drop_column("users", "document")

    op.drop_index(op.f("ix_daily_study_plan_items_date"), table_name="daily_study_plan_items")
    op.drop_index(op.f("ix_daily_study_plan_items_study_plan_id"), table_name="daily_study_plan_items")
    op.drop_table("daily_study_plan_items")
    op.drop_index(op.f("ix_study_plans_material_id"), table_name="study_plans")
    op.drop_index(op.f("ix_study_plans_child_id"), table_name="study_plans")
    op.drop_table("study_plans")

    op.drop_column("pedagogical_materials", "processing_error")
    op.drop_column("pedagogical_materials", "processing_status")
    op.drop_column("pedagogical_materials", "ai_analysis")
    op.drop_column("pedagogical_materials", "extracted_text")
    op.drop_column("pedagogical_materials", "file_url")

    op.drop_column("children", "observations")
    op.drop_column("children", "difficulties")
    op.drop_column("children", "preferences")
    op.drop_column("children", "shift")
    op.drop_column("children", "grade")
