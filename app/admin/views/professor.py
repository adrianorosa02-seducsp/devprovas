from sqladmin import ModelView

from app.models.models import Professor


class ProfessorAdmin(ModelView, model=Professor):
    name = "Professor"
    name_plural = "Professores"
    icon = "fa-solid fa-chalkboard-user"
    category = "Acadêmico"
    
    column_list = [
        Professor.usuario,
        Professor.escola,
        Professor.formacao,
        Professor.especialidade,
        Professor.ativo,
        Professor.created_at,
    ]
    column_searchable_list = [
        Professor.usuario,
    ]
    column_sortable_list = [
        Professor.ativo,
        Professor.created_at,
    ]
    column_default_sort = ("ativo", True)
    column_filters = [
        Professor.escola_id,
        Professor.ativo,
    ]
    page_size = 25
    
    form_columns = [
        Professor.usuario_id,
        Professor.escola_id,
        Professor.formacao,
        Professor.especialidade,
        Professor.ativo,
    ]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True