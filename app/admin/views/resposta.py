from sqladmin import ModelView

from app.models.models import Resposta


class RespostaAdmin(ModelView, model=Resposta):
    name = "Resposta"
    name_plural = "Respostas"
    icon = "fa-solid fa-reply"
    category = "Avaliações"
    
    column_list = [
        Resposta.questao,
        Resposta.aluno,
        Resposta.alternativa,
        Resposta.texto_dissertativo,
        Resposta.nota,
        Resposta.corrigida,
        Resposta.created_at,
    ]
    column_searchable_list = [
        Resposta.texto_dissertativo,
    ]
    column_sortable_list = [
        Resposta.questao_id,
        Resposta.aluno_id,
        Resposta.created_at,
    ]
    column_default_sort = ("created_at", True)
    column_filters = [
        Resposta.questao_id,
        Resposta.aluno_id,
        Resposta.corrigida,
    ]
    page_size = 25
    
    form_columns = [
        Resposta.questao_id,
        Resposta.aluno_id,
        Resposta.alternativa_id,
        Resposta.texto_dissertativo,
        Resposta.nota,
        Resposta.corrigida,
    ]
    form_widget_args = {
        "texto_dissertativo": {"rows": 4},
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True