"""daily learning journey

Revision ID: 202607150001
Revises: 202607140005
Create Date: 2026-07-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "202607150001"
down_revision = "202607140005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "daily_learning_sessions",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="waiting_schedule"),
        sa.Column("source", sa.String(length=30), nullable=False, server_default="system"),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("parent_guidance", sa.Text(), nullable=True),
        sa.Column("child_activity", sa.Text(), nullable=True),
        sa.Column("acknowledged_at", sa.Date(), nullable=True),
        sa.Column("context_json", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("child_id", "date", name="uq_daily_learning_session_child_date"),
    )
    op.create_index(op.f("ix_daily_learning_sessions_child_id"), "daily_learning_sessions", ["child_id"], unique=False)
    op.create_index(op.f("ix_daily_learning_sessions_date"), "daily_learning_sessions", ["date"], unique=False)

    op.create_table(
        "attendance_records",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="present"),
        sa.Column("reason", sa.String(length=180), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("child_id", "date", name="uq_attendance_record_child_date"),
    )
    op.create_index(op.f("ix_attendance_records_child_id"), "attendance_records", ["child_id"], unique=False)
    op.create_index(op.f("ix_attendance_records_date"), "attendance_records", ["date"], unique=False)

    op.create_table(
        "academic_grades",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject", sa.String(length=80), nullable=False),
        sa.Column("assessment_name", sa.String(length=120), nullable=False),
        sa.Column("assessment_date", sa.Date(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("max_score", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_academic_grades_child_id"), "academic_grades", ["child_id"], unique=False)
    op.create_index(op.f("ix_academic_grades_school_id"), "academic_grades", ["school_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_academic_grades_school_id"), table_name="academic_grades")
    op.drop_index(op.f("ix_academic_grades_child_id"), table_name="academic_grades")
    op.drop_table("academic_grades")
    op.drop_index(op.f("ix_attendance_records_date"), table_name="attendance_records")
    op.drop_index(op.f("ix_attendance_records_child_id"), table_name="attendance_records")
    op.drop_table("attendance_records")
    op.drop_index(op.f("ix_daily_learning_sessions_date"), table_name="daily_learning_sessions")
    op.drop_index(op.f("ix_daily_learning_sessions_child_id"), table_name="daily_learning_sessions")
    op.drop_table("daily_learning_sessions")
