from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.models.models import Usuario
from app.core.security import verify_password


class AdminAuth(AuthenticationBackend):
    async def login(self, request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        if not username or not password:
            return False
        
        async with async_session_maker() as session:
            result = await session.execute(
                select(Usuario).where(Usuario.email == username)
            )
            usuario = result.scalar_one_or_none()
            
            if not usuario:
                return False
            
            if not verify_password(password, usuario.senha_hash):
                return False
            
            if usuario.tipo != "admin":
                return False
            
            if not usuario.ativo:
                return False
            
            request.session["user_id"] = str(usuario.id)
            request.session["user_nome"] = usuario.nome
            request.session["user_email"] = usuario.email
        
        return True
    
    async def logout(self, request) -> bool:
        request.session.clear()
        return True
    
    async def authenticate(self, request) -> bool:
        user_id = request.session.get("user_id")
        if not user_id:
            return False
        
        async with async_session_maker() as session:
            result = await session.execute(
                select(Usuario).where(Usuario.id == user_id)
            )
            usuario = result.scalar_one_or_none()
            
            if not usuario or not usuario.ativo or usuario.tipo != "admin":
                return False
        
        return True