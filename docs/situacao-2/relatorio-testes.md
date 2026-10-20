# Relatório de testes automatizados — Situação 2

**Data da execução:** 19/10/2026
**Ambiente:** macOS (Apple Silicon), Python 3.12.15, pytest 8.4.2, pytest-cov 7.0.0, Playwright 1.55 (Chromium)
**Bancos:** SQLite em memória (unitários e integração), SQLite em arquivo (E2E) e PostgreSQL 16.2 (teste de restrições do banco)

## Como reproduzir

```bash
source .venv/bin/activate
pytest --cov                     # suíte completa (o teste de PostgreSQL é pulado sem PG_TEST_URL)
PG_TEST_URL=postgresql+psycopg://agendafacil:agendafacil@localhost:5432/agendafacil_teste pytest -m pg
pytest -m e2e                    # só os testes ponta a ponta
```

## Resumo

| Métrica | Resultado |
|---|---|
| Testes executados | **87** |
| Aprovados | **87** |
| Reprovados | 0 |
| Cobertura de código (linhas) | **97%** (meta: > 70%) |
| Tempo total | ≈ 23 s |

Sem a variável `PG_TEST_URL`, a mesma suíte mostra `86 passed, 1 skipped`: o único teste pulado é o que exige PostgreSQL.

### Distribuição por nível (Modelo V)

| Nível | Arquivos | Qtde. | O que verifica |
|---|---|---|---|
| Unitário | `tests/unit/test_models.py`, `test_validacao.py`, `test_agendamento_service.py`, `test_outros_services.py` | 56 | Models, validações de entrada e regras de negócio dos services (RN01–RN07) |
| Integração | `tests/integration/test_auth_controller.py`, `test_agendamentos_controller.py`, `test_admin_controller.py` | 27 | Controllers + templates + banco de teste: rotas, permissões por papel, CSRF, mensagens, páginas 404/403/500 |
| Integração (PostgreSQL) | `tests/integration/test_postgres.py` | 1 | Migração Alembic no PostgreSQL real e restrição `EXCLUDE` contra sobreposição |
| Sistema / ponta a ponta | `tests/e2e/test_fluxos.py` | 3 | Navegador real (Chromium): agendar, cancelar, e dois clientes disputando o mesmo horário |

## Cobertura por módulo

```
Name                                               Stmts   Miss  Cover
----------------------------------------------------------------------
src/agendafacil/__init__.py                           31      2    94%
src/agendafacil/config.py                             27      2    93%
src/agendafacil/controllers/__init__.py                8      0   100%
src/agendafacil/controllers/admin.py                  70      0   100%
src/agendafacil/controllers/agendamentos.py           79      0   100%
src/agendafacil/controllers/auth.py                   48      0   100%
src/agendafacil/controllers/erros.py                  30      5    83%
src/agendafacil/controllers/main.py                    9      0   100%
src/agendafacil/controllers/profissional.py           39      0   100%
src/agendafacil/extensions.py                          4      0   100%
src/agendafacil/filtros.py                            19      0   100%
src/agendafacil/models/__init__.py                     6      0   100%
src/agendafacil/models/agendamento.py                 35      1    97%
src/agendafacil/models/horario.py                     19      1    95%
src/agendafacil/models/profissional.py                20      1    95%
src/agendafacil/models/servico.py                     18      1    94%
src/agendafacil/models/usuario.py                     39      0   100%
src/agendafacil/relogio.py                             9      0   100%
src/agendafacil/security.py                           60      1    98%
src/agendafacil/services/__init__.py                   0      0   100%
src/agendafacil/services/agendamento_service.py       97      4    96%
src/agendafacil/services/auth_service.py              38      3    92%
src/agendafacil/services/erros.py                      8      0   100%
src/agendafacil/services/profissional_service.py      63      6    90%
src/agendafacil/services/servico_service.py           44      3    93%
src/agendafacil/services/validacao.py                 77      0   100%
----------------------------------------------------------------------
TOTAL                                                897     30    97%
```

As linhas não cobertas são, em sua maioria, ramos defensivos para condições de corrida, como o `IntegrityError` capturado depois que a checagem em Python já passou. Esse cenário é coberto indiretamente pelo teste de PostgreSQL e pelo E2E de horário ocupado.

## Lista de testes executados

| Teste | Resultado |
|---|---|
| `tests/e2e/test_fluxos.py::test_e2e_agendar_horario[chromium]` | ✅ |
| `tests/e2e/test_fluxos.py::test_e2e_cancelar_agendamento[chromium]` | ✅ |
| `tests/e2e/test_fluxos.py::test_e2e_horario_ocupado[chromium]` | ✅ |
| `tests/integration/test_admin_controller.py::test_painel_admin` | ✅ |
| `tests/integration/test_admin_controller.py::test_criar_editar_e_desativar_servico` | ✅ |
| `tests/integration/test_admin_controller.py::test_servico_invalido` | ✅ |
| `tests/integration/test_admin_controller.py::test_cadastrar_profissional` | ✅ |
| `tests/integration/test_admin_controller.py::test_admin_lista_e_cancela_qualquer_agendamento` | ✅ |
| `tests/integration/test_agendamentos_controller.py::test_fluxo_de_agendamento_em_passos` | ✅ |
| `tests/integration/test_agendamentos_controller.py::test_data_passada_e_dia_sem_horario` | ✅ |
| `tests/integration/test_agendamentos_controller.py::test_profissional_que_nao_realiza_servico_e_ignorado` | ✅ |
| `tests/integration/test_agendamentos_controller.py::test_agendar_e_listar` | ✅ |
| `tests/integration/test_agendamentos_controller.py::test_agendar_horario_ocupado` | ✅ |
| `tests/integration/test_agendamentos_controller.py::test_agendar_com_dados_incompletos` | ✅ |
| `tests/integration/test_agendamentos_controller.py::test_cancelar_pelo_cliente` | ✅ |
| `tests/integration/test_agendamentos_controller.py::test_cancelamento_tardio_e_bloqueado` | ✅ |
| `tests/integration/test_agendamentos_controller.py::test_cancelar_agendamento_de_outro_cliente` | ✅ |
| `tests/integration/test_agendamentos_controller.py::test_painel_profissional_concluir_e_cancelar` | ✅ |
| `tests/integration/test_agendamentos_controller.py::test_profissional_gerencia_horarios` | ✅ |
| `tests/integration/test_agendamentos_controller.py::test_usuario_profissional_sem_cadastro_de_profissional` | ✅ |
| `tests/integration/test_auth_controller.py::test_pagina_inicial_lista_servicos` | ✅ |
| `tests/integration/test_auth_controller.py::test_cadastro_login_logout` | ✅ |
| `tests/integration/test_auth_controller.py::test_cadastro_invalido_mostra_erros_e_mantem_dados` | ✅ |
| `tests/integration/test_auth_controller.py::test_login_invalido` | ✅ |
| `tests/integration/test_auth_controller.py::test_login_redireciona_por_papel_e_next` | ✅ |
| `tests/integration/test_auth_controller.py::test_rota_protegida_exige_login` | ✅ |
| `tests/integration/test_auth_controller.py::test_controle_de_acesso_por_papel` | ✅ |
| `tests/integration/test_auth_controller.py::test_paginas_de_erro` | ✅ |
| `tests/integration/test_auth_controller.py::test_erro_500_personalizado_e_rollback` | ✅ |
| `tests/integration/test_auth_controller.py::test_csrf_bloqueia_post_sem_token` | ✅ |
| `tests/integration/test_postgres.py::test_exclude_impede_sobreposicao_no_banco` | ✅ |
| `tests/unit/test_agendamento_service.py::test_horarios_livres_respeitam_jornada_e_duracao` | ✅ |
| `tests/unit/test_agendamento_service.py::test_horarios_livres_excluem_passado_domingo_e_servico_nao_realizado` | ✅ |
| `tests/unit/test_agendamento_service.py::test_agendar_ocupa_horario` | ✅ |
| `tests/unit/test_agendamento_service.py::test_nao_permite_sobreposicao[inicio0]` | ✅ |
| `tests/unit/test_agendamento_service.py::test_nao_permite_sobreposicao[inicio1]` | ✅ |
| `tests/unit/test_agendamento_service.py::test_nao_permite_sobreposicao[inicio2]` | ✅ |
| `tests/unit/test_agendamento_service.py::test_permite_horario_encostado` | ✅ |
| `tests/unit/test_agendamento_service.py::test_regras_de_horario[inicio0-j\xe1 passou]` | ✅ |
| `tests/unit/test_agendamento_service.py::test_regras_de_horario[inicio1-n\xe3o atende]` | ✅ |
| `tests/unit/test_agendamento_service.py::test_regras_de_horario[inicio2-n\xe3o atende]` | ✅ |
| `tests/unit/test_agendamento_service.py::test_regras_de_horario[inicio3-n\xe3o atende]` | ✅ |
| `tests/unit/test_agendamento_service.py::test_profissional_precisa_realizar_servico_e_servico_ativo` | ✅ |
| `tests/unit/test_agendamento_service.py::test_somente_cliente_agenda` | ✅ |
| `tests/unit/test_agendamento_service.py::test_cliente_cancela_com_antecedencia_e_libera_horario` | ✅ |
| `tests/unit/test_agendamento_service.py::test_cliente_nao_cancela_com_menos_de_2_horas` | ✅ |
| `tests/unit/test_agendamento_service.py::test_outro_cliente_nao_cancela` | ✅ |
| `tests/unit/test_agendamento_service.py::test_concluir_atendimento` | ✅ |
| `tests/unit/test_agendamento_service.py::test_listagens` | ✅ |
| `tests/unit/test_models.py::test_senha_e_armazenada_como_hash` | ✅ |
| `tests/unit/test_models.py::test_papeis_e_primeiro_nome` | ✅ |
| `tests/unit/test_models.py::test_preco_formatado_em_reais` | ✅ |
| `tests/unit/test_models.py::test_horario_contem_intervalo` | ✅ |
| `tests/unit/test_models.py::test_regra_de_cancelamento_2_horas[antecedencia0-True]` | ✅ |
| `tests/unit/test_models.py::test_regra_de_cancelamento_2_horas[antecedencia1-False]` | ✅ |
| `tests/unit/test_models.py::test_agendamento_cancelado_nao_pode_ser_cancelado_de_novo` | ✅ |
| `tests/unit/test_models.py::test_banco_rejeita_email_duplicado` | ✅ |
| `tests/unit/test_models.py::test_banco_rejeita_preco_ou_duracao_invalidos[preco0-30]` | ✅ |
| `tests/unit/test_models.py::test_banco_rejeita_preco_ou_duracao_invalidos[preco1-0]` | ✅ |
| `tests/unit/test_models.py::test_banco_rejeita_preco_ou_duracao_invalidos[preco2-500]` | ✅ |
| `tests/unit/test_models.py::test_banco_rejeita_dois_agendamentos_ativos_no_mesmo_inicio` | ✅ |
| `tests/unit/test_outros_services.py::test_cadastro_e_autenticacao` | ✅ |
| `tests/unit/test_outros_services.py::test_email_unico_no_cadastro` | ✅ |
| `tests/unit/test_outros_services.py::test_usuario_inativo_nao_autentica` | ✅ |
| `tests/unit/test_outros_services.py::test_papel_invalido` | ✅ |
| `tests/unit/test_outros_services.py::test_crud_servico` | ✅ |
| `tests/unit/test_outros_services.py::test_cadastrar_profissional` | ✅ |
| `tests/unit/test_outros_services.py::test_cadastrar_profissional_exige_servico_e_email_valido` | ✅ |
| `tests/unit/test_outros_services.py::test_horarios_do_profissional` | ✅ |
| `tests/unit/test_validacao.py::test_preco_aceita_formatos_brasileiros[45,00-esperado0]` | ✅ |
| `tests/unit/test_validacao.py::test_preco_aceita_formatos_brasileiros[1.234,5-esperado1]` | ✅ |
| `tests/unit/test_validacao.py::test_preco_aceita_formatos_brasileiros[R$ 30-esperado2]` | ✅ |
| `tests/unit/test_validacao.py::test_preco_aceita_formatos_brasileiros[19.9-esperado3]` | ✅ |
| `tests/unit/test_validacao.py::test_preco_invalido[abc]` | ✅ |
| `tests/unit/test_validacao.py::test_preco_invalido[0]` | ✅ |
| `tests/unit/test_validacao.py::test_preco_invalido[-5]` | ✅ |
| `tests/unit/test_validacao.py::test_preco_invalido[]` | ✅ |
| `tests/unit/test_validacao.py::test_preco_invalido[99999999]` | ✅ |
| `tests/unit/test_validacao.py::test_duracao[30-True]` | ✅ |
| `tests/unit/test_validacao.py::test_duracao[5-True]` | ✅ |
| `tests/unit/test_validacao.py::test_duracao[480-True]` | ✅ |
| `tests/unit/test_validacao.py::test_duracao[4-False]` | ✅ |
| `tests/unit/test_validacao.py::test_duracao[481-False]` | ✅ |
| `tests/unit/test_validacao.py::test_duracao[x-False]` | ✅ |
| `tests/unit/test_validacao.py::test_email_normalizado_e_validado` | ✅ |
| `tests/unit/test_validacao.py::test_nome_telefone_senha` | ✅ |
| `tests/unit/test_validacao.py::test_conversores` | ✅ |

## Verificações complementares (fora do pytest)

| Verificação | Resultado |
|---|---|
| `flask db upgrade` em SQLite e em PostgreSQL 16.2 | OK |
| `flask db check` (models × migração) | "No new upgrade operations detected." |
| `flask db downgrade base` | OK |
| DDL `03-projeto-fisico.sql` executado no PostgreSQL 16.2 | OK. Sobreposição rejeitada, intervalo encostado aceito, agendamento cancelado sobreposto aceito, preço negativo e e-mail duplicado rejeitados |
| `flask seed` | OK |
