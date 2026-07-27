"""clip escola accounts

Revision ID: 202607270001
Revises: 202607150001
Create Date: 2026-07-27
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "202607270001"
down_revision = "202607150001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "clip_escola_accounts",
        sa.Column("guardian_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_cookie_encrypted", sa.String(length=2000), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending_pairing"),
        sa.Column("qr_pairing_token", sa.String(length=255), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_message_ids", sa.JSON(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["guardian_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("guardian_id", "child_id", name="uq_clip_escola_account_guardian_child"),
    )
    op.create_index(op.f("ix_clip_escola_accounts_guardian_id"), "clip_escola_accounts", ["guardian_id"], unique=False)
    op.create_index(op.f("ix_clip_escola_accounts_child_id"), "clip_escola_accounts", ["child_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_clip_escola_accounts_child_id"), table_name="clip_escola_accounts")
    op.drop_index(op.f("ix_clip_escola_accounts_guardian_id"), table_name="clip_escola_accounts")
    op.drop_table("clip_escola_accounts")
