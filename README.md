# AgendaFácil

Sistema web de agendamento para salões e barbearias, desenvolvido no **PIT Engenharia de Software II** (Cruzeiro do Sul Virtual).

**Aluno:** Davy Gabriel Stresser Pereira · **RGM:** 36963089

| | |
|---|---|
| Aplicação em funcionamento | [PENDENTE] |
| Vídeo de apresentação | [PENDENTE] |
| Repositório | https://github.com/davystresserr/agendafacil-pit2 |

> **Sobre o PIT I:** os documentos originais do PIT I não estavam disponíveis. O planejamento (escopo, UML, IHC e dados) foi **reconstruído do zero** a partir da ideia original e revisado conforme o material do PIT II. Ver [`docs/situacao-1/escopo.md`](docs/situacao-1/escopo.md).

## Funcionalidades

- **Cliente:** cadastro, login, catálogo de serviços (preço e duração), agendamento em 4 passos com horários livres calculados, "Meus agendamentos" e cancelamento com até 2 horas de antecedência.
- **Profissional:** agenda de atendimentos, concluir/cancelar atendimentos, cadastro dos horários de trabalho.
- **Administrador:** cadastro, edição e ativação/desativação de serviços, cadastro de profissionais e visão de todos os agendamentos.
- **Regras garantidas em duas camadas:** no serviço (Python) e no PostgreSQL (`CHECK`, `UNIQUE` e `EXCLUDE` contra sobreposição de horários).

## Stack

Python 3.12 · Flask · Flask-SQLAlchemy · Flask-Migrate (Alembic) · PostgreSQL 16 · Jinja2 + HTML5/CSS3/JavaScript puro · pytest + pytest-cov + Playwright · Render (hospedagem) + Cloudflare (domínio)

## Arquitetura (MVC + serviços)

```
src/
├── wsgi.py                     # ponto de entrada (gunicorn / flask)
├── migrations/                 # Alembic (gerado a partir do DDL da Situação 1)
└── agendafacil/
    ├── models/                 # M: entidades SQLAlchemy (Usuario, Profissional, Servico, HorarioDisponivel, Agendamento)
    ├── services/               # regras de negócio e validação (sem dependência de HTTP)
    ├── controllers/            # C: blueprints Flask (auth, main, agendamentos, profissional, admin, erros)
    ├── templates/              # V: telas Jinja2
    ├── static/                 # CSS e JavaScript
    ├── security.py             # sessão, papéis, CSRF
    └── cli.py                  # flask seed
```

## Estrutura do repositório

| Pasta | Conteúdo |
|---|---|
| [`docs/situacao-1`](docs/situacao-1) | Escopo e requisitos, UML (casos de uso, classes, sequência, atividades), IHC e wireframes, modelo de dados (conceitual, lógico 3FN, físico SQL) e dicionário de dados |
| [`docs/situacao-2`](docs/situacao-2) | Relatório de testes e manual do usuário |
| [`docs/situacao-3`](docs/situacao-3) | Plano de testes (V&V), formulário para colegas, laudo de qualidade, changelog e roteiro do vídeo |
| [`docs/evidencias`](docs/evidencias) | Prints das telas (gerados com Playwright) |
| [`docs/deploy.md`](docs/deploy.md) | Deploy no Render e domínio no Cloudflare |
| `src/` | Código da aplicação |
| `tests/` | Testes unitários, de integração e ponta a ponta |
| `entrega/` | Formulário da atividade preenchido |

## Instalação (desenvolvimento)

Requisitos: Python 3.12 e Docker (para o PostgreSQL). Sem Docker, use qualquer PostgreSQL 14+ e ajuste `DATABASE_URL`.

```bash
git clone https://github.com/davystresserr/agendafacil-pit2.git
cd agendafacil-pit2
python3.12 -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                   # edite SECRET_KEY e SEED_PASSWORD
docker compose up -d                   # sobe o PostgreSQL
```

## Execução

```bash
flask --app src/wsgi.py db upgrade     # cria as tabelas
flask --app src/wsgi.py seed           # serviços, profissionais e usuários de demonstração
flask --app src/wsgi.py run --debug    # http://127.0.0.1:5000
```

Usuários de demonstração (senha = `SEED_PASSWORD` do `.env`): `admin@agendafacil.com`, `carlos@agendafacil.com`, `ana@agendafacil.com`, `cliente@agendafacil.com`.

## Testes

```bash
playwright install chromium            # uma vez, para os testes E2E
pytest --cov                           # suíte completa com cobertura
pytest -m e2e                          # só os testes ponta a ponta
PG_TEST_URL=postgresql+psycopg://agendafacil:agendafacil@localhost:5432/agendafacil_teste pytest -m pg
```

Última execução: **87 testes aprovados, cobertura de 97%**. Ver [`docs/situacao-2/relatorio-testes.md`](docs/situacao-2/relatorio-testes.md).

Scripts auxiliares:

```bash
python scripts/exportar_diagramas.py   # PNG dos diagramas Mermaid e wireframes
python scripts/gerar_evidencias.py     # prints das telas em docs/evidencias/
```

## Deploy

Render via Blueprint ([`render.yaml`](render.yaml)) + domínio no Cloudflare: passo a passo em [`docs/deploy.md`](docs/deploy.md).
