"""create phone number for user column

Revision ID: ecacd36224be
Revises: 
Create Date: 2024-10-12 08:35:10.657501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ecacd36224be'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number',sa.String(), nullable=True))


def downgrade() -> None:
    pass
