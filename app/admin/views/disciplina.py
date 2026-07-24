from sqladmin import ModelView

from app.models.models import Disciplina


class DisciplinaAdmin(ModelView, model=Disciplina):
    name = "Disciplina"
    name_plural = "Disciplinas"
    icon = "fa-solid fa-book"
    category = "Acadêmico"
    
    column_list = [
        Disciplina.nome,
        Disciplina.codigo,
        Disciplina.escola,
        Disciplina.ativo,
        Disciplina.created_at,
    ]
    column_searchable_list = [
        Disciplina.nome,
        Disciplina.codigo,
    ]
    column_sortable_list = [
        Disciplina.nome,
        Disciplina.ativo,
        Disciplina.created_at,
    ]
    column_default_sort = ("nome", False)
    column_filters = [
        Disciplina.escola_id,
        Disciplina.ativo,
    ]
    page_size = 25
    
    form_columns = [
        Disciplina.nome,
        Disciplina.codigo,
        Disciplina.escola_id,
        Disciplina.ativo,
    ]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True