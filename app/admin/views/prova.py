from sqladmin import ModelView

from app.models.models import Prova


class ProvaAdmin(ModelView, model=Prova):
    name = "Prova"
    name_plural = "Provas"
    icon = "fa-solid fa-file-pen"
    category = "Avaliações"
    
    column_list = [
        Prova.titulo,
        Prova.disciplina,
        Prova.professor,
        Prova.data_aplicacao,
        Prova.duracao_minutos,
        Prova.peso,
        Prova.ativo,
        Prova.created_at,
    ]
    column_searchable_list = [
        Prova.titulo,
        Prova.descricao,
    ]
    column_sortable_list = [
        Prova.titulo,
        Prova.data_aplicacao,
        Prova.created_at,
    ]
    column_default_sort = ("data_aplicacao", True)
    column_filters = [
        Prova.disciplina_id,
        Prova.professor_id,
        Prova.ativo,
    ]
    page_size = 25
    
    form_columns = [
        Prova.titulo,
        Prova.descricao,
        Prova.disciplina_id,
        Prova.professor_id,
        Prova.data_aplicacao,
        Prova.duracao_minutos,
        Prova.peso,
        Prova.ativo,
    ]
    form_widget_args = {
        "descricao": {"rows": 4},
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True