from sqladmin import ModelView
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models.models import Usuario
from app.core.security import hash_password


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
        "senha",
        Usuario.tipo,
        Usuario.escola_id,
        Usuario.ativo,
    ]
    form_widget_args = {
        "senha": {"type": "password"},
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True
    
    async def create_model(self, request, data: dict) -> Usuario:
        plain_password = data.pop("senha", None)
        model = await super().create_model(request, data)
        if plain_password:
            model.senha_hash = hash_password(plain_password)
            request.state.session.add(model)
            await request.state.session.flush()
        return model
    
    async def update_model(self, request, pk, data: dict) -> Usuario:
        plain_password = data.pop("senha", None)
        model = await super().update_model(request, pk, data)
        if plain_password:
            model.senha_hash = hash_password(plain_password)
            request.state.session.add(model)
            await request.state.session.flush()
        return model


def _hash_password_before_save(mapper, connection, target):
    if hasattr(target, '_plain_password') and target._plain_password:
        target.senha_hash = hash_password(target._plain_password)


event.listen(Usuario, "before_insert", _hash_password_before_save)
event.listen(Usuario, "before_update", _hash_password_before_save)