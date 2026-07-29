"""create mapa_gdrive table

Revision ID: 8f9c3d2a1b0c
Revises: 7271ea76b189
Create Date: 2026-07-29 22:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '8f9c3d2a1b0c'
down_revision: Union[str, None] = '7271ea76b189'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'mapa_gdrive',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('professor_id', sa.UUID(), nullable=False),
        sa.Column('alias_professor', sa.String(length=255), nullable=False),
        sa.Column('estrutura', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mapa_gdrive_alias'), 'mapa_gdrive', ['alias_professor'], unique=False)
    op.create_index(op.f('ix_mapa_gdrive_professor'), 'mapa_gdrive', ['professor_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_mapa_gdrive_professor'), table_name='mapa_gdrive')
    op.drop_index(op.f('ix_mapa_gdrive_alias'), table_name='mapa_gdrive')
    op.drop_table('mapa_gdrive')
