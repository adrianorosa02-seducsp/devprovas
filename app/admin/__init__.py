from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.database import async_engine
from app.admin.auth import AdminAuth
from app.admin.views import register_admin_views


def create_admin(app, engine: AsyncEngine = None) -> Admin:
    engine = engine or async_engine
    
    auth_backend = AdminAuth(secret_key="dev-secret-change-in-production")
    
    admin = Admin(
        app=app,
        engine=engine,
        title="DevProvas Admin",
        base_url="/admin",
        authentication_backend=auth_backend,
    )
    
    register_admin_views(admin)
    
    return admin