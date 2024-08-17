"""add dateofbirth column

Revision ID: e8f87fcb6e17
Revises: 
Create Date: 2024-08-17 17:36:32.146864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8f87fcb6e17'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("date_of_birth", sa.Date(), nullable=True))
    pass


def downgrade() -> None:
    op.drop_column("users", "date_of_birth")
    pass
