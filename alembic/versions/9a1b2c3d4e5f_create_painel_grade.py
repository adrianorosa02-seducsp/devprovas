"""create painel grade tables

Revision ID: 9a1b2c3d4e5f
Revises: 8f9c3d2a1b0c
Create Date: 2026-08-31 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "9a1b2c3d4e5f"
down_revision: Union[str, None] = "8f9c3d2a1b0c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "painel_configuracoes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("escola_id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("intervalo_sincronizacao_minutos", sa.Integer(), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["escola_id"], ["escolas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("escola_id"),
    )
    op.create_table(
        "fontes_grade",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("configuracao_id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("turno", sa.String(length=20), nullable=True),
        sa.Column("url_google_drive", sa.Text(), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["configuracao_id"], ["painel_configuracoes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "salas",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("escola_id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("codigo", sa.String(length=50), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["escola_id"], ["escolas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("escola_id", "nome", name="uq_sala_escola_nome"),
    )
    op.create_table(
        "plataformas",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("configuracao_id", sa.UUID(), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("tipo", sa.String(length=30), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("conteudo", sa.Text(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["configuracao_id"], ["painel_configuracoes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("configuracao_id", "ordem", name="uq_plataforma_config_ordem"),
    )
    op.create_table(
        "mensagens_painel",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("configuracao_id", sa.UUID(), nullable=False),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("conteudo", sa.Text(), nullable=False),
        sa.Column("prioridade", sa.Integer(), nullable=False),
        sa.Column("inicia_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("termina_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["configuracao_id"], ["painel_configuracoes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "importacoes_grade",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("configuracao_id", sa.UUID(), nullable=False),
        sa.Column("fonte_id", sa.UUID(), nullable=True),
        sa.Column("url_origem", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("hash_arquivo", sa.String(length=128), nullable=True),
        sa.Column("detalhes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("erro", sa.Text(), nullable=True),
        sa.Column("iniciado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("concluido_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["configuracao_id"], ["painel_configuracoes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["fonte_id"], ["fontes_grade.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "horarios_aula",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("configuracao_id", sa.UUID(), nullable=False),
        sa.Column("importacao_id", sa.UUID(), nullable=True),
        sa.Column("turma_id", sa.UUID(), nullable=False),
        sa.Column("disciplina_id", sa.UUID(), nullable=True),
        sa.Column("professor_id", sa.UUID(), nullable=True),
        sa.Column("sala_id", sa.UUID(), nullable=True),
        sa.Column("dia_semana", sa.Integer(), nullable=False),
        sa.Column("turno", sa.String(length=20), nullable=False),
        sa.Column("hora_inicio", sa.String(length=5), nullable=False),
        sa.Column("hora_fim", sa.String(length=5), nullable=False),
        sa.Column("disciplina_codigo_original", sa.String(length=20), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["configuracao_id"], ["painel_configuracoes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["importacao_id"], ["importacoes_grade.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["turma_id"], ["turmas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["disciplina_id"], ["disciplinas.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["professor_id"], ["professores.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sala_id"], ["salas.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("configuracao_id", "turma_id", "dia_semana", "hora_inicio", name="uq_horario_turma_dia_inicio"),
    )


def downgrade() -> None:
    op.drop_table("horarios_aula")
    op.drop_table("importacoes_grade")
    op.drop_table("mensagens_painel")
    op.drop_table("plataformas")
    op.drop_table("salas")
    op.drop_table("fontes_grade")
    op.drop_table("painel_configuracoes")
