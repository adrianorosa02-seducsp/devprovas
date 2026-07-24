from app.admin.views.acervo import AcervoDigitalAdmin
from app.admin.views.aprendizagem import AprendizagemEssencialAdmin
from app.admin.views.escopo import EscopoSequenciaAdmin
from app.admin.views.escola import EscolaAdmin
from app.admin.views.disciplina import DisciplinaAdmin
from app.admin.views.professor import ProfessorAdmin
from app.admin.views.turma import TurmaAdmin
from app.admin.views.usuario import UsuarioAdmin
from app.admin.views.prova import ProvaAdmin
from app.admin.views.questao import QuestaoAdmin
from app.admin.views.alternativa import AlternativaAdmin
from app.admin.views.resposta import RespostaAdmin
from app.admin.views.material import MaterialDidaticoAdmin


def register_admin_views(admin):
    admin.add_view(AcervoDigitalAdmin)
    admin.add_view(AprendizagemEssencialAdmin)
    admin.add_view(EscopoSequenciaAdmin)
    admin.add_view(EscolaAdmin)
    admin.add_view(DisciplinaAdmin)
    admin.add_view(ProfessorAdmin)
    admin.add_view(TurmaAdmin)
    admin.add_view(ProvaAdmin)
    admin.add_view(QuestaoAdmin)
    admin.add_view(AlternativaAdmin)
    admin.add_view(RespostaAdmin)
    admin.add_view(UsuarioAdmin)
    admin.add_view(MaterialDidaticoAdmin)