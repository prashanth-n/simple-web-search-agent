"""initial schema

Revision ID: 20260328_01
Revises:
Create Date: 2026-03-28 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260328_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agents_slug", "agents", ["slug"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=150), nullable=False),
        sa.Column("google_sub", sa.String(length=255), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("google_sub"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_index("ix_users_google_sub", "users", ["google_sub"], unique=False)

    for table_name in [
        "generic_research_runs",
        "startup_analysis_runs",
        "marketing_analysis_runs",
        "product_competitor_analysis_runs",
        "financial_analysis_runs",
    ]:
        op.create_table(
            table_name,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("agent_id", sa.Integer(), nullable=False),
            sa.Column("query", sa.String(length=500), nullable=False),
            sa.Column("results", sa.JSON(), nullable=False),
            sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
            sa.ForeignKeyConstraint(["agent_id"], ["agents.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(f"ix_{table_name}_id", table_name, ["id"], unique=False)
        op.create_index(f"ix_{table_name}_user_id", table_name, ["user_id"], unique=False)
        op.create_index(f"ix_{table_name}_agent_id", table_name, ["agent_id"], unique=False)
        op.create_index(f"ix_{table_name}_query", table_name, ["query"], unique=False)

    op.create_table(
        "chat_threads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_threads_id", "chat_threads", ["id"], unique=False)
    op.create_index("ix_chat_threads_user_id", "chat_threads", ["user_id"], unique=False)
    op.create_index("ix_chat_threads_agent_id", "chat_threads", ["agent_id"], unique=False)

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("thread_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("message_type", sa.String(length=50), nullable=False, server_default="text"),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["thread_id"], ["chat_threads.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_messages_id", "chat_messages", ["id"], unique=False)
    op.create_index("ix_chat_messages_user_id", "chat_messages", ["user_id"], unique=False)
    op.create_index("ix_chat_messages_thread_id", "chat_messages", ["thread_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_chat_messages_thread_id", table_name="chat_messages")
    op.drop_index("ix_chat_messages_user_id", table_name="chat_messages")
    op.drop_index("ix_chat_messages_id", table_name="chat_messages")
    op.drop_table("chat_messages")

    op.drop_index("ix_chat_threads_agent_id", table_name="chat_threads")
    op.drop_index("ix_chat_threads_user_id", table_name="chat_threads")
    op.drop_index("ix_chat_threads_id", table_name="chat_threads")
    op.drop_table("chat_threads")

    for table_name in [
        "financial_analysis_runs",
        "product_competitor_analysis_runs",
        "marketing_analysis_runs",
        "startup_analysis_runs",
        "generic_research_runs",
    ]:
        op.drop_index(f"ix_{table_name}_query", table_name=table_name)
        op.drop_index(f"ix_{table_name}_agent_id", table_name=table_name)
        op.drop_index(f"ix_{table_name}_user_id", table_name=table_name)
        op.drop_index(f"ix_{table_name}_id", table_name=table_name)
        op.drop_table(table_name)

    op.drop_index("ix_users_google_sub", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_agents_slug", table_name="agents")
    op.drop_table("agents")
