"""adaptive learning, integrations and gamification tables

Revision ID: 202607140001
Revises: 202607130002
Create Date: 2026-07-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202607140001"
down_revision: str | None = "202607130002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- Adaptive learning (Fase C) ---
    op.create_table(
        "learning_profiles",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("visual_preference", sa.Float(), nullable=False),
        sa.Column("auditory_preference", sa.Float(), nullable=False),
        sa.Column("kinesthetic_preference", sa.Float(), nullable=False),
        sa.Column("learning_speed", sa.Float(), nullable=False),
        sa.Column("confidence_level", sa.Integer(), nullable=False),
        sa.Column("retention_rate", sa.Float(), nullable=False),
        sa.Column("competencies", sa.JSON(), nullable=False),
        sa.Column("identified_challenges", sa.JSON(), nullable=False),
        sa.Column("engagement_level", sa.Integer(), nullable=False),
        sa.Column("last_auto_update", sa.DateTime(timezone=True), nullable=True),
        sa.Column("use_adaptive_difficulty", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("child_id"),
    )
    op.create_index(op.f("ix_learning_profiles_child_id"), "learning_profiles", ["child_id"], unique=True)

    op.create_table(
        "learning_histories",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("interaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("response_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("theme", sa.String(length=180), nullable=False),
        sa.Column("activity_type", sa.String(length=50), nullable=False),
        sa.Column("difficulty_presented", sa.String(length=20), nullable=False),
        sa.Column("was_successful", sa.Boolean(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("time_spent_seconds", sa.Integer(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("effective_styles", sa.JSON(), nullable=False),
        sa.Column("activity_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.ForeignKeyConstraint(["interaction_id"], ["interactions.id"]),
        sa.ForeignKeyConstraint(["response_id"], ["interaction_responses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_learning_histories_child_id"), "learning_histories", ["child_id"], unique=False)
    op.create_index(op.f("ix_learning_histories_theme"), "learning_histories", ["theme"], unique=False)
    op.create_index(op.f("ix_learning_histories_activity_date"), "learning_histories", ["activity_date"], unique=False)

    op.create_table(
        "adaptive_recommendations",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("learning_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recommended_theme", sa.String(length=180), nullable=False),
        sa.Column("recommended_difficulty", sa.String(length=20), nullable=False),
        sa.Column("recommended_style", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("predicted_success_rate", sa.Float(), nullable=False),
        sa.Column("risk_of_dropout", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.ForeignKeyConstraint(["learning_profile_id"], ["learning_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_adaptive_recommendations_child_id"), "adaptive_recommendations", ["child_id"], unique=False)
    op.create_index(op.f("ix_adaptive_recommendations_learning_profile_id"), "adaptive_recommendations", ["learning_profile_id"], unique=False)

    # --- Integrações externas (Fase I) ---
    op.create_table(
        "integrations",
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("credentials", sa.JSON(), nullable=True),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("webhook_url", sa.String(length=500), nullable=True),
        sa.Column("webhook_secret", sa.String(length=255), nullable=True),
        sa.Column("last_sync", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sync_enabled", sa.Boolean(), nullable=False),
        sa.Column("sync_interval_minutes", sa.Integer(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_integrations_school_id"), "integrations", ["school_id"], unique=False)

    op.create_table(
        "integration_sync_logs",
        sa.Column("integration_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("records_synced", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["integration_id"], ["integrations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_integration_sync_logs_integration_id"), "integration_sync_logs", ["integration_id"], unique=False)

    op.create_table(
        "webhook_events",
        sa.Column("integration_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("processed", sa.Boolean(), nullable=False),
        sa.Column("error", sa.String(length=500), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["integration_id"], ["integrations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_webhook_events_integration_id"), "webhook_events", ["integration_id"], unique=False)

    op.create_table(
        "google_classroom_syncs",
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("classroom_id", sa.String(length=100), nullable=False),
        sa.Column("classroom_name", sa.String(length=255), nullable=False),
        sa.Column("teacher_email", sa.String(length=255), nullable=False),
        sa.Column("mapped_class_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sync_assignments", sa.Boolean(), nullable=False),
        sa.Column("sync_grades", sa.Boolean(), nullable=False),
        sa.Column("sync_announcements", sa.Boolean(), nullable=False),
        sa.Column("last_assignment_sync", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_grade_sync", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.ForeignKeyConstraint(["mapped_class_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("classroom_id"),
    )
    op.create_index(op.f("ix_google_classroom_syncs_school_id"), "google_classroom_syncs", ["school_id"], unique=False)

    op.create_table(
        "microsoft_teams_syncs",
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("team_id", sa.String(length=100), nullable=False),
        sa.Column("team_name", sa.String(length=255), nullable=False),
        sa.Column("channel_id", sa.String(length=100), nullable=False),
        sa.Column("channel_name", sa.String(length=255), nullable=False),
        sa.Column("mapped_class_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sync_assignments", sa.Boolean(), nullable=False),
        sa.Column("sync_messages", sa.Boolean(), nullable=False),
        sa.Column("post_to_channel", sa.Boolean(), nullable=False),
        sa.Column("last_sync", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.ForeignKeyConstraint(["mapped_class_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("team_id"),
    )
    op.create_index(op.f("ix_microsoft_teams_syncs_school_id"), "microsoft_teams_syncs", ["school_id"], unique=False)

    op.create_table(
        "whatsapp_business_syncs",
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phone_number_id", sa.String(length=50), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("guardian_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("send_notifications", sa.Boolean(), nullable=False),
        sa.Column("send_grades", sa.Boolean(), nullable=False),
        sa.Column("send_assignments", sa.Boolean(), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.ForeignKeyConstraint(["guardian_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone_number_id"),
    )
    op.create_index(op.f("ix_whatsapp_business_syncs_school_id"), "whatsapp_business_syncs", ["school_id"], unique=False)

    op.create_table(
        "webhook_subscriptions",
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("secret", sa.String(length=255), nullable=False),
        sa.Column("events", sa.JSON(), nullable=False),
        sa.Column("filters", sa.JSON(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("total_delivered", sa.Integer(), nullable=False),
        sa.Column("total_failed", sa.Integer(), nullable=False),
        sa.Column("last_delivery", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_webhook_subscriptions_school_id"), "webhook_subscriptions", ["school_id"], unique=False)

    # --- Gamificação (Fase J) ---
    op.create_table(
        "badges",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("badge_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("icon_emoji", sa.String(length=10), nullable=False),
        sa.Column("unlock_criteria", sa.JSON(), nullable=True),
        sa.Column("points_awarded", sa.Integer(), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("rarity", sa.String(length=20), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_badges_child_id"), "badges", ["child_id"], unique=False)

    op.create_table(
        "missions",
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("reward_points", sa.Integer(), nullable=False),
        sa.Column("reward_badge", sa.String(length=50), nullable=True),
        sa.Column("required_activity_count", sa.Integer(), nullable=False),
        sa.Column("required_score", sa.Float(), nullable=False),
        sa.Column("required_theme", sa.String(length=100), nullable=True),
        sa.Column("time_limit_days", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("difficulty", sa.String(length=20), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_missions_school_id"), "missions", ["school_id"], unique=False)

    op.create_table(
        "mission_completions",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("progress", sa.Float(), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("points_earned", sa.Integer(), nullable=False),
        sa.Column("badge_earned", sa.String(length=50), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.ForeignKeyConstraint(["mission_id"], ["missions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mission_completions_child_id"), "mission_completions", ["child_id"], unique=False)
    op.create_index(op.f("ix_mission_completions_mission_id"), "mission_completions", ["mission_id"], unique=False)

    op.create_table(
        "leaderboards",
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("total_points", sa.Integer(), nullable=False),
        sa.Column("week_points", sa.Integer(), nullable=False),
        sa.Column("month_points", sa.Integer(), nullable=False),
        sa.Column("overall_rank", sa.Integer(), nullable=True),
        sa.Column("week_rank", sa.Integer(), nullable=True),
        sa.Column("month_rank", sa.Integer(), nullable=True),
        sa.Column("current_streak", sa.Integer(), nullable=False),
        sa.Column("longest_streak", sa.Integer(), nullable=False),
        sa.Column("last_activity", sa.DateTime(timezone=True), nullable=True),
        sa.Column("badge_count", sa.Integer(), nullable=False),
        sa.Column("epic_badge_count", sa.Integer(), nullable=False),
        sa.Column("legendary_badge_count", sa.Integer(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("child_id"),
    )
    op.create_index(op.f("ix_leaderboards_school_id"), "leaderboards", ["school_id"], unique=False)
    op.create_index(op.f("ix_leaderboards_child_id"), "leaderboards", ["child_id"], unique=True)

    op.create_table(
        "achievements",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("criteria", sa.JSON(), nullable=False),
        sa.Column("points_awarded", sa.Integer(), nullable=False),
        sa.Column("badge_icon", sa.String(length=10), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_secret", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_achievements_child_id"), "achievements", ["child_id"], unique=False)

    op.create_table(
        "daily_challenges",
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("challenge_type", sa.String(length=50), nullable=False),
        sa.Column("required_theme", sa.String(length=100), nullable=True),
        sa.Column("required_count", sa.Integer(), nullable=False),
        sa.Column("required_score", sa.Float(), nullable=False),
        sa.Column("bonus_points", sa.Integer(), nullable=False),
        sa.Column("reward_badge", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_daily_challenges_school_id"), "daily_challenges", ["school_id"], unique=False)
    op.create_index(op.f("ix_daily_challenges_date"), "daily_challenges", ["date"], unique=False)

    op.create_table(
        "daily_challenge_completions",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("challenge_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("points_earned", sa.Integer(), nullable=False),
        sa.Column("badge_earned", sa.String(length=50), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.ForeignKeyConstraint(["challenge_id"], ["daily_challenges.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_daily_challenge_completions_child_id"), "daily_challenge_completions", ["child_id"], unique=False)
    op.create_index(op.f("ix_daily_challenge_completions_challenge_id"), "daily_challenge_completions", ["challenge_id"], unique=False)

    op.create_table(
        "rewards",
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("icon", sa.String(length=10), nullable=False),
        sa.Column("cost_points", sa.Integer(), nullable=False),
        sa.Column("reward_type", sa.String(length=50), nullable=False),
        sa.Column("reward_data", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("available_count", sa.Integer(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rewards_school_id"), "rewards", ["school_id"], unique=False)

    op.create_table(
        "reward_claims",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reward_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("points_spent", sa.Integer(), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivered", sa.Boolean(), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.ForeignKeyConstraint(["reward_id"], ["rewards.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reward_claims_child_id"), "reward_claims", ["child_id"], unique=False)
    op.create_index(op.f("ix_reward_claims_reward_id"), "reward_claims", ["reward_id"], unique=False)


def downgrade() -> None:
    op.drop_table("reward_claims")
    op.drop_table("rewards")
    op.drop_table("daily_challenge_completions")
    op.drop_table("daily_challenges")
    op.drop_table("achievements")
    op.drop_table("leaderboards")
    op.drop_table("mission_completions")
    op.drop_table("missions")
    op.drop_table("badges")

    op.drop_table("webhook_subscriptions")
    op.drop_table("whatsapp_business_syncs")
    op.drop_table("microsoft_teams_syncs")
    op.drop_table("google_classroom_syncs")
    op.drop_table("webhook_events")
    op.drop_table("integration_sync_logs")
    op.drop_table("integrations")

    op.drop_table("adaptive_recommendations")
    op.drop_table("learning_histories")
    op.drop_table("learning_profiles")
