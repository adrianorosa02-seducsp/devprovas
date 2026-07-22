"""create escopo_sequencia table

Revision ID: 687223ddaf6b
Revises: 
Create Date: 2026-07-20 19:31:34.438978
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '687223ddaf6b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('escopo_sequencia',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('ano_referencia', sa.Integer(), nullable=False),
    sa.Column('etapa', sa.String(length=20), nullable=False),
    sa.Column('componente', sa.String(length=50), nullable=False),
    sa.Column('ano', sa.Integer(), nullable=False),
    sa.Column('id_ae', sa.String(length=20), nullable=False),
    sa.Column('prefixo_ae', sa.String(length=10), nullable=False),
    sa.Column('id_aula', sa.String(length=30), nullable=False),
    sa.Column('aula', sa.String(length=20), nullable=True),
    sa.Column('conteudo', sa.Text(), nullable=True),
    sa.Column('objetivos_aprendizagem', sa.Text(), nullable=True),
    sa.Column('habilidades', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('aprendizagem_essencial', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('pagina_pdf', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ano_referencia', 'id_aula', 'aula', 'pagina_pdf', name='uq_escopo_sequencia')
    )
    op.create_index(op.f('ix_escopo_sequencia_ano'), 'escopo_sequencia', ['ano'], unique=False)
    op.create_index(op.f('ix_escopo_sequencia_ano_referencia'), 'escopo_sequencia', ['ano_referencia'], unique=False)
    op.create_index(op.f('ix_escopo_sequencia_componente'), 'escopo_sequencia', ['componente'], unique=False)
    op.create_index(op.f('ix_escopo_sequencia_etapa'), 'escopo_sequencia', ['etapa'], unique=False)
    op.create_index(op.f('ix_escopo_sequencia_id_ae'), 'escopo_sequencia', ['id_ae'], unique=False)
    op.create_index(op.f('ix_escopo_sequencia_id_aula'), 'escopo_sequencia', ['id_aula'], unique=False)
    op.create_index(op.f('ix_escopo_sequencia_prefixo_ae'), 'escopo_sequencia', ['prefixo_ae'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_escopo_sequencia_prefixo_ae'), table_name='escopo_sequencia')
    op.drop_index(op.f('ix_escopo_sequencia_id_aula'), table_name='escopo_sequencia')
    op.drop_index(op.f('ix_escopo_sequencia_id_ae'), table_name='escopo_sequencia')
    op.drop_index(op.f('ix_escopo_sequencia_etapa'), table_name='escopo_sequencia')
    op.drop_index(op.f('ix_escopo_sequencia_componente'), table_name='escopo_sequencia')
    op.drop_index(op.f('ix_escopo_sequencia_ano_referencia'), table_name='escopo_sequencia')
    op.drop_index(op.f('ix_escopo_sequencia_ano'), table_name='escopo_sequencia')
    op.drop_table('escopo_sequencia')