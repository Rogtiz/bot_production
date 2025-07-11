"""nickname for players

Revision ID: 37c60fa8b42a
Revises: ce5de51c17e3
Create Date: 2025-06-18 12:45:50.739510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37c60fa8b42a'
down_revision: Union[str, None] = 'ce5de51c17e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('players', sa.Column('nickname', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'players', ['nickname'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'players', type_='unique')
    op.drop_column('players', 'nickname')
    # ### end Alembic commands ###
