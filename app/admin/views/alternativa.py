from sqladmin import ModelView

from app.models.models import Alternativa


class AlternativaAdmin(ModelView, model=Alternativa):
    name = "Alternativa"
    name_plural = "Alternativas"
    icon = "fa-solid fa-circle-check"
    category = "Avaliações"
    
    column_list = [
        Alternativa.questao,
        Alternativa.letra,
        Alternativa.texto,
        Alternativa.correta,
        Alternativa.created_at,
    ]
    column_searchable_list = [
        Alternativa.texto,
    ]
    column_sortable_list = [
        Alternativa.questao_id,
        Alternativa.letra,
        Alternativa.created_at,
    ]
    column_default_sort = ("letra", False)
    column_filters = [
        Alternativa.questao_id,
        Alternativa.correta,
    ]
    page_size = 25
    
    form_columns = [
        Alternativa.questao_id,
        Alternativa.texto,
        Alternativa.correta,
        Alternativa.letra,
    ]
    form_widget_args = {
        "texto": {"rows": 3},
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True