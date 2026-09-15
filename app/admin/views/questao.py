from sqladmin import ModelView

from app.models.models import Questao


class QuestaoAdmin(ModelView, model=Questao):
    name = "Questão"
    name_plural = "Questões"
    icon = "fa-solid fa-question"
    category = "Avaliações"
    
    column_list = [
        Questao.prova,
        Questao.enunciado,
        Questao.tipo,
        Questao.pontos,
        Questao.ordem,
        Questao.created_at,
    ]
    column_searchable_list = [
        Questao.enunciado,
    ]
    column_sortable_list = [
        Questao.prova_id,
        Questao.ordem,
        Questao.created_at,
    ]
    column_default_sort = ("ordem", False)
    column_filters = [
        Questao.prova_id,
        Questao.tipo,
    ]
    page_size = 25
    
    form_columns = [
        Questao.prova_id,
        Questao.enunciado,
        Questao.tipo,
        Questao.pontos,
        Questao.ordem,
    ]
    form_widget_args = {
        "enunciado": {"rows": 6},
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True