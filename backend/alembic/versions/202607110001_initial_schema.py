"""initial schema

Revision ID: 202607110001
Revises:
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202607110001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "schools",
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("document", sa.String(length=32), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document"),
    )
    op.create_table(
        "users",
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)
    op.create_index(op.f("ix_users_school_id"), "users", ["school_id"], unique=False)
    op.create_table(
        "children",
        sa.Column("full_name", sa.String(length=180), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_name", sa.String(length=80), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_children_school_id"), "children", ["school_id"], unique=False)
    op.create_table(
        "audit_logs",
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ["actor_user_id", "action", "entity_type", "entity_id", "school_id", "created_at"]:
        op.create_index(f"ix_audit_logs_{column}", "audit_logs", [column], unique=False)
    op.create_table(
        "child_guardians",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("guardian_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relationship_type", sa.String(length=40), nullable=False),
        sa.Column("can_view", sa.Boolean(), nullable=False),
        sa.Column("can_manage_routine", sa.Boolean(), nullable=False),
        sa.Column("can_mark_notifications", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.ForeignKeyConstraint(["guardian_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("child_id", "guardian_id", name="uq_child_guardian"),
    )
    op.create_index(op.f("ix_child_guardians_child_id"), "child_guardians", ["child_id"], unique=False)
    op.create_index(op.f("ix_child_guardians_guardian_id"), "child_guardians", ["guardian_id"], unique=False)
    op.create_table(
        "routine_items",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("scheduled_time", sa.Time(), nullable=False),
        sa.Column("weekdays", sa.JSON(), nullable=False),
        sa.Column("target_audience", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_routine_items_child_id"), "routine_items", ["child_id"], unique=False)
    op.create_table(
        "tasks",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tasks_child_id"), "tasks", ["child_id"], unique=False)
    op.create_index(op.f("ix_tasks_status"), "tasks", ["status"], unique=False)
    op.create_table(
        "evolution_events",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("event_metadata", sa.JSON(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_evolution_events_child_id"), "evolution_events", ["child_id"], unique=False)
    op.create_index(op.f("ix_evolution_events_event_type"), "evolution_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_evolution_events_occurred_at"), "evolution_events", ["occurred_at"], unique=False)
    op.create_table(
        "notifications",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("routine_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("target_audience", sa.String(length=32), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.ForeignKeyConstraint(["routine_item_id"], ["routine_items.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("routine_item_id", "scheduled_at", name="uq_notification_routine_scheduled"),
    )
    op.create_index(op.f("ix_notifications_child_id"), "notifications", ["child_id"], unique=False)
    op.create_index(op.f("ix_notifications_routine_item_id"), "notifications", ["routine_item_id"], unique=False)
    op.create_index(op.f("ix_notifications_scheduled_at"), "notifications", ["scheduled_at"], unique=False)
    op.create_index(op.f("ix_notifications_status"), "notifications", ["status"], unique=False)


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("evolution_events")
    op.drop_table("tasks")
    op.drop_table("routine_items")
    op.drop_table("child_guardians")
    op.drop_table("audit_logs")
    op.drop_table("children")
    op.drop_table("users")
    op.drop_table("schools")

