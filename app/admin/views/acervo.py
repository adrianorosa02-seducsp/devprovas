from sqladmin import ModelView, action
from sqlalchemy import select
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from starlette.concurrency import run_in_threadpool

from app.models.models import AcervoDigital
from app.core.database import async_session_maker


class AcervoDigitalAdmin(ModelView, model=AcervoDigital):
    name = "Acervo Digital"
    name_plural = "Acervo Digital"
    icon = "fa-solid fa-database"
    category = "Acervo Digital"
    
    column_list = [
        AcervoDigital.arquivo_id,
        AcervoDigital.titulo,
        AcervoDigital.tipo_arquivo,
        AcervoDigital.created_at,
        AcervoDigital.updated_at,
    ]
    column_searchable_list = [AcervoDigital.arquivo_id, AcervoDigital.titulo, AcervoDigital.descricao]
    column_sortable_list = [AcervoDigital.arquivo_id, AcervoDigital.titulo, AcervoDigital.created_at]
    column_default_sort = ("created_at", True)
    column_filters = [AcervoDigital.tipo_arquivo]
    page_size = 25
    
    form_columns = [
        AcervoDigital.arquivo_id,
        AcervoDigital.titulo,
        AcervoDigital.descricao,
        AcervoDigital.tipo_arquivo,
        AcervoDigital.link_google_drive,
        AcervoDigital.link_download_python,
    ]
    form_widget_args = {
        "descricao": {"rows": 4},
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True
    
    @action(
        name="processar",
        label="Processar",
        confirmation_message="Executar o script de processamento para este item do acervo?",
        add_in_detail=True,
        add_in_list=True,
    )
    async def action_processar(self, request: Request):
        pks = request.query_params.getlist("pks")
        
        if not pks:
            return JSONResponse({"error": "Nenhum item selecionado"}, status_code=400)
        
        async with async_session_maker() as session:
            for pk in pks:
                result = await session.execute(
                    select(AcervoDigital).where(AcervoDigital.id == pk)
                )
                acervo = result.scalar_one_or_none()
                
                if acervo:
                    await run_in_threadpool(self._executar_processamento, acervo)
        
        return RedirectResponse(request.url_for("admin:list", identity=self.identity), status_code=303)
    
    def _executar_processamento(self, acervo: AcervoDigital):
        try:
            if acervo.arquivo_id and "aprendizagem" in acervo.arquivo_id.lower():
                from scripts.importar_aprendizagens_essenciais import main as import_ae
                import_ae()
            elif acervo.arquivo_id and "escopo" in acervo.arquivo_id.lower():
                from scripts.importar_escopo_sequencia import main as import_escopo
                import_escopo()
        except Exception as e:
            print(f"Erro ao processar {acervo.arquivo_id}: {e}")
            raise