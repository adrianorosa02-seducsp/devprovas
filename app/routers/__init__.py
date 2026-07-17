# from .aulas import router as aulas_router  # TODO: fix missing AulaConteudo model
# from .bncc import router as bncc_router  # TODO: fix missing Bncc models
from .acervo import router as acervo_router
from .aprendizagem import router as aprendizagem_router
from .auth import router as auth_router
from .disciplinas import router as disciplinas_router
from .escolas import router as escolas_router
from .materiais import router as materiais_router
from .professores import router as professores_router
from .provas import router as provas_router
from .questoes import router as questoes_router
from .respostas import router as respostas_router
from .turmas import router as turmas_router
from .usuarios import router as usuarios_router
