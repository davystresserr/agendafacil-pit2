# Plano de testes — Verificação e Validação (V&V)

**Sistema:** AgendaFácil · **Versão testada:** 1.0.0 · **Data de execução:** 19/10/2026 · **Responsável:** Davy Gabriel Stresser Pereira

## 1. Estratégia

Seguindo o Modelo V do material da disciplina:

| Lado do V | Atividade | Como foi feita no projeto |
|---|---|---|
| **Verificação** (o produto está sendo construído corretamente?) | Revisões e inspeções | Revisão dos requisitos contra o código; `flask db check` (models × migração); DDL executado no PostgreSQL; inspeção dos diagramas × implementação |
| | Teste unitário | pytest nos models, validações e services |
| | Teste de integração | pytest com cliente HTTP do Flask + banco de teste; migração e restrições no PostgreSQL |
| **Validação** (construímos o produto certo?) | Teste de sistema | Playwright (navegador real) nos fluxos completos |
| | Teste de aceitação | 5 colegas usando o sistema publicado, com o [formulário](formulario-colegas.md) e o roteiro; os resultados vão para o [laudo](laudo-qualidade.md) |

**Critério de aprovação da versão:** 100% dos casos de teste automatizados aprovados, cobertura > 70% e nenhum defeito de severidade **Crítica** ou **Alta** aberto após os testes dos colegas.

## 2. Casos de teste

Coluna **Automação**: arquivo e teste que executam o caso. Coluna **Resultado obtido**: o que aconteceu na execução de 19/10/2026 (`pytest`: 87 aprovados, 0 reprovados; ver [relatório](../situacao-2/relatorio-testes.md)).

### 2.1 Autenticação e acesso

| ID | Requisito | Pré-condições | Passos | Resultado esperado | Resultado obtido | Automação |
|---|---|---|---|---|---|---|
| CT-01 | RF01 | E-mail não cadastrado | 1. Abrir /cadastro 2. Preencher nome, e-mail, senha (8+) e confirmação iguais 3. Clicar "Criar conta" | Conta criada, usuário logado, mensagem "Conta criada com sucesso!" | ✅ Conforme esperado | `integration/test_auth_controller.py::test_cadastro_login_logout` |
| CT-02 | RN05 | Já existe ana@teste.com | Cadastrar com o mesmo e-mail e senha curta | Status 400; mensagens "já está cadastrado" e "pelo menos 8 caracteres"; nome digitado preservado | ✅ Conforme esperado | `test_auth_controller.py::test_cadastro_invalido_mostra_erros_e_mantem_dados`, `unit/test_outros_services.py::test_email_unico_no_cadastro`, `unit/test_models.py::test_banco_rejeita_email_duplicado` |
| CT-03 | RF02 | Usuário cadastrado | Login com senha errada | Status 401, "E-mail ou senha incorretos." (não revela se o e-mail existe) | ✅ Conforme esperado | `test_auth_controller.py::test_login_invalido` |
| CT-04 | RF02 | Usuários dos 3 papéis | Login com cada papel | Cliente → início; profissional → /profissional/; admin → /admin/ | ✅ Conforme esperado | `test_auth_controller.py::test_login_redireciona_por_papel_e_next` |
| CT-05 | RNF03 | — | Login com `?next=https://malicioso.com` | Redireciona para "/" (bloqueia redirecionamento externo) | ✅ Conforme esperado | idem CT-04 |
| CT-06 | RNF03 | Logado como cliente | Acessar /admin/ e /profissional/ | Página 403 "Acesso negado" | ✅ Conforme esperado | `test_auth_controller.py::test_controle_de_acesso_por_papel` |
| CT-07 | RNF03 | Não logado | Acessar /meus-agendamentos | Redireciona para /login com aviso | ✅ Conforme esperado | `test_auth_controller.py::test_rota_protegida_exige_login` |
| CT-08 | RNF03 | CSRF ativo | POST /login sem token; depois com token válido | Sem token: "Sua sessão expirou"; com token: segue para a autenticação | ✅ Conforme esperado | `test_auth_controller.py::test_csrf_bloqueia_post_sem_token` |
| CT-09 | RNF02 | — | Definir senha e inspecionar o registro | `senha_hash` diferente da senha; verificação correta/incorreta funciona | ✅ Conforme esperado | `unit/test_models.py::test_senha_e_armazenada_como_hash` |

### 2.2 Serviços e catálogo

| ID | Requisito | Pré-condições | Passos | Resultado esperado | Resultado obtido | Automação |
|---|---|---|---|---|---|---|
| CT-10 | RF03 | Serviços cadastrados | Abrir "/" | Lista com nome, preço em R$ e duração | ✅ Conforme esperado | `test_auth_controller.py::test_pagina_inicial_lista_servicos` |
| CT-11 | RF12 | Logado como admin | Criar serviço "Pigmentação", R$ 35,50, 40 min; editar; desativar | Mensagens de sucesso; serviço some da página inicial ao ser desativado | ✅ Conforme esperado | `integration/test_admin_controller.py::test_criar_editar_e_desativar_servico` |
| CT-12 | RN04 | Logado como admin | Criar serviço com preço 0 e duração 1000 | Status 400, "maior que zero" e "entre 5 e 480" | ✅ Conforme esperado | `test_admin_controller.py::test_servico_invalido`, `unit/test_validacao.py`, `unit/test_models.py::test_banco_rejeita_preco_ou_duracao_invalidos` |
| CT-13 | RF12 | Serviço "Barba" existe | Renomear outro serviço para "Barba" | "Já existe um serviço com este nome." | ✅ Conforme esperado | `test_admin_controller.py::test_servico_invalido` |

### 2.3 Agendamento

| ID | Requisito | Pré-condições | Passos | Resultado esperado | Resultado obtido | Automação |
|---|---|---|---|---|---|---|
| CT-14 | RF04/RF05 | Profissional com jornada seg–sáb 9–12 e 13–18 | Escolher serviço → profissional → terça | Horários de 09:00 a 11:30 e de 13:00 a 17:30 (30 min); 12:00 e 18:00 ausentes | ✅ Conforme esperado | `unit/test_agendamento_service.py::test_horarios_livres_respeitam_jornada_e_duracao`, `integration/test_agendamentos_controller.py::test_fluxo_de_agendamento_em_passos` |
| CT-15 | RN01 | Serviço de 60 min | Consultar horários | 11:00 disponível, 11:30 não (terminaria 12:30) | ✅ Conforme esperado | idem CT-14 |
| CT-16 | RN06 | "Agora" = seg 10:10 | Consultar horários de hoje; consultar domingo | Só horários futuros (a partir de 10:30); domingo sem horários | ✅ Conforme esperado | `test_agendamento_service.py::test_horarios_livres_excluem_passado_domingo_e_servico_nao_realizado` |
| CT-17 | RF04 | Cliente logado | Confirmar terça 10:00 | Redireciona a "Meus agendamentos" com "Agendamento confirmado"; 10:00 some da lista de livres | ✅ Conforme esperado | `test_agendamentos_controller.py::test_agendar_e_listar`, `test_agendamento_service.py::test_agendar_ocupa_horario`, **E2E** `e2e/test_fluxos.py::test_e2e_agendar_horario` |
| CT-18 | RN02/RF06 | 10:00–10:30 já reservado | Tentar 10:00, 09:45 e 10:15 | "Este horário acabou de ser ocupado"; nada é gravado | ✅ Conforme esperado | `test_agendamento_service.py::test_nao_permite_sobreposicao`, `test_agendamentos_controller.py::test_agendar_horario_ocupado` |
| CT-19 | RN02 | 10:00–10:30 reservado | Agendar 10:30 | Aceito (intervalos encostados não conflitam) | ✅ Conforme esperado | `test_agendamento_service.py::test_permite_horario_encostado` |
| CT-20 | RN02 | Dois clientes em navegadores diferentes | Ambos abrem o mesmo horário; A confirma; B confirma | A: confirmado; B: "acabou de ser ocupado" e o horário some da lista de B | ✅ Conforme esperado | **E2E** `e2e/test_fluxos.py::test_e2e_horario_ocupado` |
| CT-21 | RN02/RNF10 | PostgreSQL com a migração aplicada | Inserir direto no banco um agendamento sobreposto | Banco rejeita com `ex_ag_sem_sobreposicao`; intervalo encostado aceito | ✅ Conforme esperado | `integration/test_postgres.py::test_exclude_impede_sobreposicao_no_banco` |
| CT-22 | RN06 | — | Agendar no passado, às 07:00, às 11:45 (passa de 12:00) e no domingo | Mensagens "já passou" / "não atende nesse horário" | ✅ Conforme esperado | `test_agendamento_service.py::test_regras_de_horario` |
| CT-23 | RN07 | Profissional não faz "Escova" | Agendar Escova com ele | "Este profissional não realiza o serviço escolhido." | ✅ Conforme esperado | `test_agendamento_service.py::test_profissional_precisa_realizar_servico_e_servico_ativo` |
| CT-24 | RF04 | Cliente logado | POST /agendar sem profissional/horário | "Escolha serviço, profissional e horário." | ✅ Conforme esperado | `test_agendamentos_controller.py::test_agendar_com_dados_incompletos` |

### 2.4 Cancelamento

| ID | Requisito | Pré-condições | Passos | Resultado esperado | Resultado obtido | Automação |
|---|---|---|---|---|---|---|
| CT-25 | RF08/RN03 | Agendamento a mais de 2h | Clicar "Cancelar" → "Sim, confirmar" | "Agendamento cancelado. O horário foi liberado."; status Cancelado; horário volta a ficar livre | ✅ Conforme esperado | `test_agendamentos_controller.py::test_cancelar_pelo_cliente`, `test_agendamento_service.py::test_cliente_cancela_com_antecedencia_e_libera_horario`, **E2E** `test_e2e_cancelar_agendamento` |
| CT-26 | RN03 | Agendamento daqui a 1h30 | Ver lista; tentar cancelar por POST | Botão substituído por aviso; POST retorna "2 horas de antecedência"; status continua Agendado | ✅ Conforme esperado | `test_agendamentos_controller.py::test_cancelamento_tardio_e_bloqueado`, `unit/test_models.py::test_regra_de_cancelamento_2_horas` (limite exato de 2h00 aceito; 1h59 recusado) |
| CT-27 | RN03 | Agendamento a 30 min | Profissional cancela | Permitido | ✅ Conforme esperado | `test_agendamento_service.py::test_cliente_nao_cancela_com_menos_de_2_horas` |
| CT-28 | RNF03 | Agendamento de outro cliente | Tentar cancelar | "Você não tem permissão..."; id inexistente → 404 | ✅ Conforme esperado | `test_agendamentos_controller.py::test_cancelar_agendamento_de_outro_cliente` |

### 2.5 Profissional e administrador

| ID | Requisito | Pré-condições | Passos | Resultado esperado | Resultado obtido | Automação |
|---|---|---|---|---|---|---|
| CT-29 | RF09/RF11 | Agendamentos do profissional | Abrir painel; concluir antes e depois do início | Agenda listada; antes: "ainda não começou"; depois: "concluído" | ✅ Conforme esperado | `test_agendamentos_controller.py::test_painel_profissional_concluir_e_cancelar` |
| CT-30 | RF10 | Logado como profissional | Adicionar domingo 10–12; tentar 11–13; remover | "Horário adicionado."; "se sobrepõe"; "Horário removido." | ✅ Conforme esperado | `test_agendamentos_controller.py::test_profissional_gerencia_horarios` |
| CT-31 | RF13 | Logado como admin | Cadastrar profissional com serviço; repetir e-mail | Sucesso; depois "já está cadastrado" com dados preservados | ✅ Conforme esperado | `test_admin_controller.py::test_cadastrar_profissional` |
| CT-32 | RF13 | — | Cadastrar profissional sem serviços | "Selecione pelo menos um serviço." | ✅ Conforme esperado | `unit/test_outros_services.py::test_cadastrar_profissional_exige_servico_e_email_valido` |
| CT-33 | RF14 | Agendamento existente | Admin abre /admin/agendamentos e cancela | Lista mostra o agendamento; cancelamento permitido | ✅ Conforme esperado | `test_admin_controller.py::test_admin_lista_e_cancela_qualquer_agendamento` |

### 2.6 Tratamento de erros e IHC

| ID | Requisito | Pré-condições | Passos | Resultado esperado | Resultado obtido | Automação |
|---|---|---|---|---|---|---|
| CT-34 | IHC | — | Acessar URL inexistente | Página 404 personalizada com "Voltar ao início" | ✅ Conforme esperado | `test_auth_controller.py::test_paginas_de_erro` |
| CT-35 | IHC | Rota que lança exceção | Acessar a rota | Página 500 personalizada; transação desfeita | ✅ Conforme esperado | `test_auth_controller.py::test_erro_500_personalizado_e_rollback` |
| CT-36 | RNF05 | Navegador | Cadastro com confirmação de senha diferente | Campo destacado e "As senhas não conferem" antes do envio | ✅ Conforme esperado (inspeção visual) | Print `docs/evidencias/04-cadastro-validacao-cliente.png` (script Playwright) |
| CT-37 | RNF05 | Celular 390 px | Abrir início, menu e "Meus agendamentos" | Layout em coluna, menu ☰, tabela em cartões, sem rolagem horizontal | ✅ Conforme esperado (inspeção visual) | Prints `20-mobile-servicos.png`, `21-mobile-meus-agendamentos.png`, `22-mobile-menu.png` |

## 3. Verificação estática (revisões e inspeções)

| ID | Item verificado | Método | Resultado obtido |
|---|---|---|---|
| VR-01 | Models × migração Alembic | `flask db check` | Na primeira execução, divergência no nome de 2 índices (defeito **D-02** do laudo, corrigido). Depois: "No new upgrade operations detected." |
| VR-02 | DDL do projeto físico | Execução do `.sql` no PostgreSQL 16.2 | Na primeira execução, a extensão `btree_gist` não estava disponível (defeito **D-01**, corrigido). Depois: OK, com todas as restrições validadas por inserts de teste |
| VR-03 | Requisitos × casos de teste | Rastreabilidade (seção 2) | Todos os RF01–RF14 e RN01–RN07 têm ao menos um caso de teste |
| VR-04 | Diagramas × código | Inspeção | Classes, atributos e associações conferem com `src/agendafacil/models` |
| VR-05 | Segurança | Inspeção | Hash de senha, CSRF, controle por papel, cookies `HttpOnly`/`Secure` (produção), ORM parametrizado, sem segredos no repositório (`.env` no `.gitignore`) |

## 4. Validação com usuários (teste de aceitação)

| ID | Testador | Data | Resultado |
|---|---|---|---|
| VA-01 | Colega 1 | [PENDENTE: aguardando teste real] | [PENDENTE] |
| VA-02 | Colega 2 | [PENDENTE: aguardando teste real] | [PENDENTE] |
| VA-03 | Colega 3 | [PENDENTE: aguardando teste real] | [PENDENTE] |
| VA-04 | Colega 4 | [PENDENTE: aguardando teste real] | [PENDENTE] |
| VA-05 | Colega 5 | [PENDENTE: aguardando teste real] | [PENDENTE] |

Os detalhes de cada teste ficam em [`laudo-qualidade.md`](laudo-qualidade.md).
