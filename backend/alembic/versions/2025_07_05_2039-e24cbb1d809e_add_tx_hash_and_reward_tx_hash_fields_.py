"""Add tx_hash and reward_tx_hash fields to allowances table

Revision ID: e24cbb1d809e
Revises: fadd94301e16
Create Date: 2025-07-05 20:39:31.787836

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e24cbb1d809e'
down_revision: Union[str, Sequence[str], None] = 'fadd94301e16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('idx_audit_log_ip_address'), table_name='audit_log')
    op.drop_index(op.f('idx_audit_log_timestamp'), table_name='audit_log')
    op.drop_table('audit_log')
    op.add_column('allowances', sa.Column('tx_hash', sa.String(66), nullable=True))
    op.add_column('allowances', sa.Column('reward_tx_hash', sa.String(66), nullable=True))
    op.add_column('allowances', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('allowances', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Update existing rows with current timestamp
    op.execute("UPDATE allowances SET created_at = NOW(), updated_at = NOW() WHERE created_at IS NULL")
    
    # Now make the columns NOT NULL
    op.alter_column('allowances', 'created_at', nullable=False)
    op.alter_column('allowances', 'updated_at', nullable=False)
    op.drop_index(op.f('idx_allowances_order_id'), table_name='allowances')
    op.drop_index(op.f('idx_allowances_status'), table_name='allowances')
    op.drop_index(op.f('idx_allowances_timestamp'), table_name='allowances')
    op.create_index(op.f('ix_allowances_timestamp'), 'allowances', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_allowances_timestamp'), table_name='allowances')
    op.create_index(op.f('idx_allowances_timestamp'), 'allowances', ['timestamp'], unique=False)
    op.create_index(op.f('idx_allowances_status'), 'allowances', ['status'], unique=False)
    op.create_index(op.f('idx_allowances_order_id'), 'allowances', ['order_id'], unique=False)
    op.drop_column('allowances', 'updated_at')
    op.drop_column('allowances', 'created_at')
    op.drop_column('allowances', 'reward_tx_hash')
    op.drop_column('allowances', 'tx_hash')
    op.create_table('audit_log',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('ip_address', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('user_agent', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('request_body_hash', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('audit_log_pkey'))
    )
    op.create_index(op.f('idx_audit_log_timestamp'), 'audit_log', ['timestamp'], unique=False)
    op.create_index(op.f('idx_audit_log_ip_address'), 'audit_log', ['ip_address'], unique=False)
    # ### end Alembic commands ###
