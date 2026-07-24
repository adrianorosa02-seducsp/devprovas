from sqladmin import ModelView

from app.models.models import MaterialDidatico


class MaterialDidaticoAdmin(ModelView, model=MaterialDidatico):
    name = "Material Didático"
    name_plural = "Materiais Didáticos"
    icon = "fa-solid fa-file-pdf"
    category = "Materiais"
    
    column_list = [
        MaterialDidatico.id_aula,
        MaterialDidatico.titulo,
        MaterialDidatico.ano_referencia,
        MaterialDidatico.bimestre,
        MaterialDidatico.serie,
        MaterialDidatico.componente,
        MaterialDidatico.tipo,
    ]
    column_searchable_list = [
        MaterialDidatico.id_aula,
        MaterialDidatico.titulo,
        MaterialDidatico.tipo,
    ]
    column_sortable_list = [
        MaterialDidatico.ano_referencia,
        MaterialDidatico.bimestre,
        MaterialDidatico.serie,
        MaterialDidatico.componente,
    ]
    column_default_sort = ("ano_referencia", True)
    column_filters = [
        MaterialDidatico.ano_referencia,
        MaterialDidatico.bimestre,
        MaterialDidatico.serie,
        MaterialDidatico.componente,
    ]
    page_size = 25
    
    form_columns = [
        MaterialDidatico.ano_referencia,
        MaterialDidatico.bimestre,
        MaterialDidatico.serie,
        MaterialDidatico.componente,
        MaterialDidatico.cod_cronograma,
        MaterialDidatico.id_cronograma,
        MaterialDidatico.titulo,
        MaterialDidatico.referencia_id,
        MaterialDidatico.tipo,
        MaterialDidatico.ordenacao,
        MaterialDidatico.semana,
        MaterialDidatico.aulas_com_tarefa,
        MaterialDidatico.link_url_youtube,
        MaterialDidatico.exibir_municipio,
        MaterialDidatico.arquivos,
        MaterialDidatico.array_links_youtube,
        MaterialDidatico.id_aula,
    ]
    form_widget_args = {
        "array_links_youtube": {"rows": 4},
        "arquivos": {"rows": 4},
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True