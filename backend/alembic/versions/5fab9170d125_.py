"""empty message

Revision ID: 5fab9170d125
Revises: 
Create Date: 2025-07-02 11:59:48.142875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5fab9170d125'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('health_check_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ping_time', sa.Float(), nullable=True),
    sa.Column('delivered_packages_percentage', sa.Integer(), nullable=True),
    sa.Column('last_successful_ping_timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('host_addresses',
    sa.Column('ip_address', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('ip_address')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('host_addresses')
    op.drop_table('health_check_history')
    # ### end Alembic commands ###
