"""add chat memories

Revision ID: 20260328_02
Revises: 20260328_01
Create Date: 2026-03-28 00:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260328_02"
down_revision = "20260328_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_memories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("thread_id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("memory_type", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("source_message_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"]),
        sa.ForeignKeyConstraint(["source_message_id"], ["chat_messages.id"]),
        sa.ForeignKeyConstraint(["thread_id"], ["chat_threads.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_memories_id", "chat_memories", ["id"], unique=False)
    op.create_index("ix_chat_memories_user_id", "chat_memories", ["user_id"], unique=False)
    op.create_index("ix_chat_memories_thread_id", "chat_memories", ["thread_id"], unique=False)
    op.create_index("ix_chat_memories_agent_id", "chat_memories", ["agent_id"], unique=False)
    op.create_index("ix_chat_memories_memory_type", "chat_memories", ["memory_type"], unique=False)
    op.create_index("ix_chat_memories_source_message_id", "chat_memories", ["source_message_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_chat_memories_source_message_id", table_name="chat_memories")
    op.drop_index("ix_chat_memories_memory_type", table_name="chat_memories")
    op.drop_index("ix_chat_memories_agent_id", table_name="chat_memories")
    op.drop_index("ix_chat_memories_thread_id", table_name="chat_memories")
    op.drop_index("ix_chat_memories_user_id", table_name="chat_memories")
    op.drop_index("ix_chat_memories_id", table_name="chat_memories")
    op.drop_table("chat_memories")
