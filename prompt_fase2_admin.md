# Prompt Mestre – Desenvolvimento da Plataforma DevProvas

## Visão Geral

Estamos desenvolvendo uma plataforma denominada **DevProvas**, cujo objetivo é consolidar todas as informações pedagógicas da SEDUC em uma base de conhecimento estruturada, servindo de origem para geração automática de documentos pedagógicos, planos de aula, sequências didáticas, análises, APIs e ferramentas de apoio ao professor.

O projeto deve ser desenvolvido utilizando **Python** como linguagem principal, **FastAPI** como framework web, **SQLAlchemy** como ORM e **PostgreSQL** como banco de dados.

Toda a arquitetura deverá privilegiar reutilização, modularização e manutenção de longo prazo.

---

# Filosofia do Projeto

O banco de dados **não é apenas um repositório**.

Ele representa uma **Base de Conhecimento Pedagógica**.

Cada documento oficial importado deverá enriquecer essa base.

Os documentos (PDFs) são apenas a origem dos dados.

Depois de importados, nunca mais dependeremos deles para consultas.

Toda consulta deverá ocorrer sobre o PostgreSQL.

---

# Tecnologias

Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* PostgreSQL
* Pydantic

Frontend

* Jinja2
* HTMX
* Bootstrap 5

Não utilizar React, Angular ou Vue.

Toda a aplicação deverá permanecer dentro do ecossistema Python.

---

# Estrutura Geral

```
PDF
        │
        ▼
Importadores
        │
        ▼
Banco PostgreSQL
        │
        ▼
Views Pedagógicas
        │
        ▼
API
        │
        ▼
Interface Administrativa
        │
        ▼
Aplicações consumidoras
```

---

# Estrutura do Projeto

```
app/

    admin/

        dashboard/

        routers/

        templates/

        static/

        services/

        forms/

    core/

    models/

    routers/

    schemas/

    services/

    extractors/

scripts/

infra/
```

---

# Interface Administrativa

A interface administrativa deverá funcionar de forma semelhante ao conceito utilizado pelo Odoo.

Entretanto, não será utilizado o Odoo.

Será desenvolvido um framework administrativo próprio.

Objetivos:

* Dashboard
* CRUD automático
* Filtros
* Pesquisa
* Paginação
* Execução de scripts Python
* Administração do banco

---

# Dashboard

A primeira tela deverá possuir módulos como:

* Acervo Digital
* BNCC
* Aprendizagens Essenciais
* Escopo-Sequência
* Professores
* Escolas
* Turmas
* Materiais Digitais
* Importadores
* Configurações

---

# Primeiro módulo

O primeiro módulo administrativo será:

**Acervo Digital**

Ele será responsável pela origem de todos os processos de importação.

Funções:

* Cadastro
* Alteração
* Exclusão
* Pesquisa
* Visualização
* Execução do processamento

O botão **Processar** executará diretamente os scripts Python já existentes.

Não haverá duplicação de código.

---

# Framework Administrativo

A ideia é construir um framework reutilizável.

No futuro, para criar um novo módulo administrativo bastará registrar o Model.

Exemplo:

```
class Professor(Base):
```

Automaticamente deverão existir:

* Listagem
* Cadastro
* Alteração
* Exclusão
* Pesquisa
* Paginação

---

# Banco de Dados

O banco deverá permanecer totalmente normalizado.

As tabelas representam entidades distintas.

Exemplos:

* BNCC
* Aprendizagens Essenciais
* Escopo-Sequência
* Professores
* Escolas
* Turmas
* Materiais Digitais
* Acervo Digital

---

# BNCC

A tabela BNCC será considerada a **Fonte da Verdade**.

Ela conterá todas as descrições oficiais.

Toda habilidade deverá ser referenciada pela BNCC.

Jamais duplicar descrições.

---

# Aprendizagens Essenciais

Cada Aprendizagem Essencial possui:

* id_ae
* prefixo
* codigo_ae
* descricao

Relacionamentos

* habilidade_priorizada

JSONB

* habilidades_relacionadas
* conhecimentos_previos
* prova_paulista
* saresp
* desenvolvimento_aprendizagem

---

# Escopo-Sequência

O Escopo-Sequência não deverá duplicar informações.

Ele armazenará apenas:

* Aula
* Conteúdo
* Objetivos
* Habilidades
* Aprendizagem Essencial

A coluna Habilidades referencia BNCC.

A coluna Aprendizagem Essencial referencia Aprendizagens Essenciais.

---

# Relacionamentos

```
BNCC
   │
   ▼
Aprendizagens Essenciais
   │
   ▼
Escopo-Sequência
```

---

# Estratégia de Importação

Os PDFs serão processados em etapas.

Primeiro:

Aprendizagens Essenciais

Depois:

Escopo-Sequência

Jamais processar tudo simultaneamente.

Cada etapa deverá ser totalmente validada antes da persistência.

---

# Estratégia de Desenvolvimento

Sempre trabalhar incrementalmente.

Nunca reescrever código já validado.

Quando uma etapa estiver funcionando, ela será considerada concluída.

O próximo desenvolvimento deverá partir da etapa anterior.

---

# Regras durante o desenvolvimento

* Uma única solução por resposta.
* Não apresentar alternativas sem solicitação.
* Não reescrever arquitetura consolidada.
* Alterações mínimas.
* Reaproveitar código existente.
* Priorizar simplicidade.
* Priorizar legibilidade.
* Evitar duplicação.

---

# Persistência

Os importadores deverão possuir duas responsabilidades apenas:

1. Extrair.

2. Persistir.

Toda regra de negócio ficará em Services.

---

# Views

As aplicações consumidoras não consultarão diretamente as tabelas.

Serão criadas Views específicas.

Exemplo:

```
vw_plano_aula
```

Essa View consolidará informações provenientes de:

* Escopo-Sequência
* Aprendizagens Essenciais
* BNCC
* Materiais Digitais

Assim o Plano de Aula poderá ser gerado com uma única consulta.

---

# Plano de Aula

O Plano de Aula deverá apresentar:

* Aula
* Conteúdo
* Objetivos
* Descrição da AE
* Descrição da BNCC
* Conhecimentos prévios
* Prova Paulista
* SARESP
* Bloco temático
* Livro do estudante
* Materiais digitais

O documento nunca deverá exibir apenas códigos.

Ele deverá apresentar todas as descrições necessárias para facilitar o trabalho do professor.

---

# Objetivo Final

Construir uma Plataforma Pedagógica capaz de:

* importar documentos oficiais;
* consolidar conhecimento pedagógico;
* administrar esse conhecimento por meio de uma interface web;
* gerar automaticamente documentos pedagógicos;
* fornecer APIs para aplicações externas;
* servir como base para futuros agentes inteligentes de apoio ao professor.

Todo o desenvolvimento deverá preservar esta arquitetura e estas estratégias como referência principal do projeto.
