"""Initial schema: users, email_analyses, analysis_feedbacks.

Revision ID: 0001
Revises:
Create Date: 2026-09-19
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.Column("is_deleted", sa.Boolean, nullable=False, default=False),
        sa.Column("username", sa.String(80), nullable=False, unique=True),
        sa.Column("email", sa.String(120), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
    )

    # ── email_analyses ────────────────────────────────────────────────────────
    op.create_table(
        "email_analyses",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.Column("is_deleted", sa.Boolean, nullable=False, default=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("email_content", sa.Text, nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("suggested_response", sa.Text, nullable=False),
        sa.Column("processing_time_ms", sa.Integer, nullable=True),
        sa.Column("model_used", sa.String(100), nullable=True),
    )
    op.create_index("ix_email_analyses_content_hash", "email_analyses", ["content_hash"])

    # ── analysis_feedbacks ────────────────────────────────────────────────────
    op.create_table(
        "analysis_feedbacks",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.Column("is_deleted", sa.Boolean, nullable=False, default=False),
        sa.Column(
            "analysis_id",
            sa.Integer,
            sa.ForeignKey("email_analyses.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("approved", sa.Boolean, nullable=False),
        sa.Column("corrected_category", sa.String(50), nullable=True),
        sa.Column("corrected_summary", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_analysis_feedbacks_analysis_id", "analysis_feedbacks", ["analysis_id"]
    )


def downgrade() -> None:
    op.drop_table("analysis_feedbacks")
    op.drop_index("ix_email_analyses_content_hash", "email_analyses")
    op.drop_table("email_analyses")
    op.drop_table("users")
