from sqladmin import ModelView

from app.models.models import Usuario


class UsuarioAdmin(ModelView, model=Usuario):
    name = "Usuário"
    name_plural = "Usuários"
    icon = "fa-solid fa-user"
    category = "Sistema"
    
    column_list = [
        Usuario.nome,
        Usuario.email,
        Usuario.tipo,
        Usuario.escola,
        Usuario.ativo,
        Usuario.created_at,
    ]
    column_searchable_list = [
        Usuario.nome,
        Usuario.email,
    ]
    column_sortable_list = [
        Usuario.tipo,
        Usuario.ativo,
        Usuario.created_at,
    ]
    column_default_sort = ("tipo", False)
    column_filters = [
        Usuario.escola_id,
        Usuario.tipo,
        Usuario.ativo,
    ]
    page_size = 25
    
    form_columns = [
        Usuario.nome,
        Usuario.email,
        Usuario.senha_hash,
        Usuario.tipo,
        Usuario.escola_id,
        Usuario.ativo,
    ]
    form_widget_args = {
        "senha_hash": {"type": "password"},
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True