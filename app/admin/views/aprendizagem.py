from sqladmin import ModelView

from app.models.models import AprendizagemEssencial


class AprendizagemEssencialAdmin(ModelView, model=AprendizagemEssencial):
    name = "Aprendizagem Essencial"
    name_plural = "Aprendizagens Essenciais"
    icon = "fa-solid fa-graduation-cap"
    category = "BNCC"
    
    column_list = [
        AprendizagemEssencial.id_ae,
        AprendizagemEssencial.prefixo,
        AprendizagemEssencial.codigo_ae,
        AprendizagemEssencial.ano_referencia,
        AprendizagemEssencial.etapa,
        AprendizagemEssencial.componente,
        AprendizagemEssencial.ano,
        AprendizagemEssencial.habilidade_priorizada,
    ]
    column_searchable_list = [
        AprendizagemEssencial.id_ae,
        AprendizagemEssencial.prefixo,
        AprendizagemEssencial.codigo_ae,
        AprendizagemEssencial.descricao,
        AprendizagemEssencial.habilidade_priorizada,
    ]
    column_sortable_list = [
        AprendizagemEssencial.id_ae,
        AprendizagemEssencial.prefixo,
        AprendizagemEssencial.ano_referencia,
        AprendizagemEssencial.etapa,
        AprendizagemEssencial.componente,
        AprendizagemEssencial.ano,
    ]
    column_default_sort = ("prefixo", True)
    column_filters = [
        AprendizagemEssencial.ano_referencia,
        AprendizagemEssencial.etapa,
        AprendizagemEssencial.componente,
        AprendizagemEssencial.ano,
    ]
    page_size = 50
    
    form_columns = [
        AprendizagemEssencial.ano_referencia,
        AprendizagemEssencial.etapa,
        AprendizagemEssencial.componente,
        AprendizagemEssencial.ano,
        AprendizagemEssencial.id_ae,
        AprendizagemEssencial.prefixo,
        AprendizagemEssencial.codigo_ae,
        AprendizagemEssencial.descricao,
        AprendizagemEssencial.habilidade_priorizada,
        AprendizagemEssencial.habilidades_relacionadas,
        AprendizagemEssencial.conhecimentos_previos,
        AprendizagemEssencial.prova_paulista,
        AprendizagemEssencial.saresp,
        AprendizagemEssencial.desenvolvimento_aprendizagem,
    ]
    form_widget_args = {
        "descricao": {"rows": 4},
        "habilidades_relacionadas": {"rows": 6},
        "conhecimentos_previos": {"rows": 4},
        "prova_paulista": {"rows": 4},
        "saresp": {"rows": 4},
        "desenvolvimento_aprendizagem": {"rows": 6},
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True