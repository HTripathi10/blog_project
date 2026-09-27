"""add post cover image url

Revision ID: a1b2c3d4e5f6
Revises: efdd4be38076
Create Date: 2026-09-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "efdd4be38076"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("cover_image_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("posts", "cover_image_url")
