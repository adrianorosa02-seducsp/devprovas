from sqladmin import ModelView

from app.models.models import Escola


class EscolaAdmin(ModelView, model=Escola):
    name = "Escola"
    name_plural = "Escolas"
    icon = "fa-solid fa-building"
    category = "Acadêmico"
    
    column_list = [
        Escola.nome,
        Escola.endereco,
        Escola.telefone,
        Escola.email,
        Escola.created_at,
    ]
    column_searchable_list = [
        Escola.nome,
        Escola.email,
    ]
    column_sortable_list = [
        Escola.nome,
        Escola.created_at,
    ]
    column_default_sort = ("nome", False)
    page_size = 25
    
    form_columns = [
        Escola.nome,
        Escola.endereco,
        Escola.telefone,
        Escola.email,
    ]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True