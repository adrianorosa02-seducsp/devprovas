from sqladmin import ModelView

from app.models.models import EscopoSequencia


class EscopoSequenciaAdmin(ModelView, model=EscopoSequencia):
    name = "Escopo-Sequência"
    name_plural = "Escopo-Sequência"
    icon = "fa-solid fa-sitemap"
    category = "BNCC"
    
    column_list = [
        EscopoSequencia.id_aula,
        EscopoSequencia.aula,
        EscopoSequencia.conteudo,
        EscopoSequencia.objetivos_aprendizagem,
        EscopoSequencia.ano_referencia,
        EscopoSequencia.etapa,
        EscopoSequencia.componente,
        EscopoSequencia.ano,
        EscopoSequencia.bimestre,
        EscopoSequencia.prefixo_ae,
        EscopoSequencia.id_ae,
        EscopoSequencia.pagina_pdf,
        EscopoSequencia.created_at,
    ]
    column_searchable_list = [
        EscopoSequencia.id_aula,
        EscopoSequencia.aula,
        EscopoSequencia.conteudo,
        EscopoSequencia.objetivos_aprendizagem,
        EscopoSequencia.id_ae,
        EscopoSequencia.prefixo_ae,
    ]
    column_sortable_list = [
        EscopoSequencia.ano_referencia,
        EscopoSequencia.etapa,
        EscopoSequencia.componente,
        EscopoSequencia.ano,
        EscopoSequencia.bimestre,
        EscopoSequencia.id_aula,
        EscopoSequencia.pagina_pdf,
        EscopoSequencia.created_at,
    ]
    column_default_sort = ("ano_referencia", True)
    column_filters = [
        EscopoSequencia.ano_referencia,
        EscopoSequencia.etapa,
        EscopoSequencia.componente,
        EscopoSequencia.ano,
        EscopoSequencia.bimestre,
    ]
    page_size = 25
    
    form_columns = [
        EscopoSequencia.ano_referencia,
        EscopoSequencia.etapa,
        EscopoSequencia.componente,
        EscopoSequencia.ano,
        EscopoSequencia.bimestre,
        EscopoSequencia.id_ae,
        EscopoSequencia.prefixo_ae,
        EscopoSequencia.id_aula,
        EscopoSequencia.aula,
        EscopoSequencia.conteudo,
        EscopoSequencia.objetivos_aprendizagem,
        EscopoSequencia.habilidades,
        EscopoSequencia.aprendizagem_essencial,
        EscopoSequencia.pagina_pdf,
    ]
    form_widget_args = {
        "conteudo": {"rows": 4},
        "objetivos_aprendizagem": {"rows": 4},
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True