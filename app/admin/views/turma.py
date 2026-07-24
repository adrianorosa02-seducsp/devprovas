from sqladmin import ModelView

from app.models.models import Turma


class TurmaAdmin(ModelView, model=Turma):
    name = "Turma"
    name_plural = "Turmas"
    icon = "fa-solid fa-users"
    category = "Acadêmico"
    
    column_list = [
        Turma.nome,
        Turma.serie,
        Turma.turno,
        Turma.escola,
        Turma.professor,
        Turma.ativo,
        Turma.created_at,
    ]
    column_searchable_list = [
        Turma.nome,
    ]
    column_sortable_list = [
        Turma.serie,
        Turma.turno,
        Turma.ativo,
        Turma.created_at,
    ]
    column_default_sort = ("serie", False)
    column_filters = [
        Turma.escola_id,
        Turma.professor_id,
        Turma.ativo,
    ]
    page_size = 25
    
    form_columns = [
        Turma.nome,
        Turma.serie,
        Turma.turno,
        Turma.escola_id,
        Turma.professor_id,
        Turma.ativo,
    ]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True