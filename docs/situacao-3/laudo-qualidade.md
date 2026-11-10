# Laudo de qualidade — AgendaFácil

**Versão avaliada:** 1.0.0 · **Responsável:** Davy Gabriel Stresser Pereira (RGM 36963089) · **Emissão:** 19/10/2026 (parcial: aguardando os testes dos colegas)

## 1. Resumo

| Indicador | Valor |
|---|---|
| Casos de teste automatizados | 99 executados, 98 aprovados e 1 pulado (o de PostgreSQL, que roda só com banco configurado) ([relatório](../situacao-2/relatorio-testes.md)) |
| Cobertura de código | 96% |
| Casos de teste do plano (CT-01 a CT-37) | 37 aprovados ([plano](plano-testes.md)) |
| Defeitos encontrados na verificação interna | 4 (todos corrigidos), seção 3 |
| Testes de aceitação com colegas | 4 de 5 realizados, seção 4 (colega 5: [PENDENTE: aguardando teste real]) |
| Defeitos apontados pelos colegas | 1 corrigido (C-01); 1 relato encerrado sem defeito (C-02), seção 5 |

**Escala de severidade**

| Severidade | Critério |
|---|---|
| Crítica | Impede o uso do sistema ou corrompe dados (ex.: dois clientes no mesmo horário). |
| Alta | Uma funcionalidade principal não funciona e não há alternativa. |
| Média | A funcionalidade funciona com falhas ou há alternativa. |
| Baixa | Problema visual, de texto ou de conforto de uso. |

## 2. Evidências das funcionalidades (versão 1.0.0)

Prints gerados automaticamente com Playwright (`python scripts/gerar_evidencias.py`), em `docs/evidencias/`:

| Funcionalidade | Evidência |
|---|---|
| Lista de serviços | ![](../evidencias/01-lista-servicos.png) |
| Login e erro de login | [02-login.png](../evidencias/02-login.png) · [03-login-erro.png](../evidencias/03-login-erro.png) |
| Validação no cliente (senhas diferentes) | [04-cadastro-validacao-cliente.png](../evidencias/04-cadastro-validacao-cliente.png) |
| Validação no servidor (e-mail duplicado) | [05-cadastro-email-duplicado.png](../evidencias/05-cadastro-email-duplicado.png) |
| Agendamento em passos | [06](../evidencias/06-agendar-passo1-servico.png) · [07](../evidencias/07-agendar-passo2-profissional.png) · [08](../evidencias/08-agendar-passo3-horarios.png) |
| Agendamento confirmado | [09-agendamento-confirmado.png](../evidencias/09-agendamento-confirmado.png) |
| Confirmação e cancelamento | [10-cancelar-confirmacao.png](../evidencias/10-cancelar-confirmacao.png) · [11-agendamento-cancelado.png](../evidencias/11-agendamento-cancelado.png) |
| Horário ocupado (dois clientes) | [12-horario-ocupado.png](../evidencias/12-horario-ocupado.png) |
| Erros 404 e 403 | [13-pagina-404.png](../evidencias/13-pagina-404.png) · [14-acesso-negado-403.png](../evidencias/14-acesso-negado-403.png) |
| Painel do profissional | [15-painel-profissional.png](../evidencias/15-painel-profissional.png) |
| Painel do administrador | [16-painel-admin.png](../evidencias/16-painel-admin.png) · [17-admin-servico-invalido.png](../evidencias/17-admin-servico-invalido.png) · [18-admin-profissionais.png](../evidencias/18-admin-profissionais.png) · [19-admin-agendamentos.png](../evidencias/19-admin-agendamentos.png) |
| Responsivo (celular) | [20-mobile-servicos.png](../evidencias/20-mobile-servicos.png) · [21-mobile-meus-agendamentos.png](../evidencias/21-mobile-meus-agendamentos.png) · [22-mobile-menu.png](../evidencias/22-mobile-menu.png) |

## 3. Defeitos encontrados na verificação interna (desenvolvedor)

Defeitos reais encontrados por mim durante a verificação (revisões, `flask db check`, execução do DDL e testes automatizados), antes da entrega aos colegas.

| ID | Descrição | Evidência | Severidade | Correção aplicada | Status |
|---|---|---|---|---|---|
| D-01 | O DDL dependia da extensão `btree_gist` para a restrição `EXCLUDE`. Num PostgreSQL sem essa extensão o script falhava na primeira linha e nenhuma tabela era criada. | Saída do `psql`: `ERROR: extension "btree_gist" is not available` (VR-02 do plano de testes) | Alta | A restrição passou a usar `int4range(profissional_id, profissional_id, '[]') WITH =`, que é nativo do GiST. A extensão deixou de ser necessária no DDL e na migração. | Corrigido e verificado (CT-21) |
| D-02 | Os nomes de 2 índices nos models (`ix_agendamentos_servico_id`, `ix_profissional_servico_servico_id`) divergiam do DDL (`ix_ag_servico`, `ix_ps_servico`); uma futura `flask db migrate` geraria uma migração indevida. | Saída do `flask db check`: `New upgrade operations detected` (VR-01) | Média | Índices declarados explicitamente nos models com os nomes do DDL. | Corrigido: `No new upgrade operations detected.` |
| D-03 | No diagrama de casos de uso exportado em PNG, os rótulos `<<include>>` e `<<extend>>` apareciam como `<>`, porque o texto era tratado como tag HTML. | `docs/situacao-1/uml/casos-de-uso.png` (versão anterior) | Baixa | Rótulos trocados por guillemets («include», «extend») e PNG regenerado. | Corrigido |
| D-04 | Teste E2E de cancelamento falhava: o seletor do card "Barba" também casava com "Corte + barba" (strict mode do Playwright). Era defeito do teste, não do sistema. | Saída do pytest: `strict mode violation ... resolved to 2 elements` | Baixa | O seletor passou a casar o título exato do card. | Corrigido: 3/3 E2E aprovados |

## 4. Testes de aceitação com colegas

> Cada colega seguiu o roteiro do [formulário](formulario-colegas.md), respondido pelo Google Forms entre 28 e 31/10/2026. As respostas abaixo resumem o que cada um escreveu; trechos entre aspas são literais.

### 4.1 Colega 1

| Campo | Resposta |
|---|---|
| Nome | Andrew |
| Data do teste e dispositivo | 28/10/2026 · celular Android + Chrome |
| O que testou e funcionou | Parte A completa (A1 a A15): todos OK. "Tudo funcionando." |
| O que testou e não funcionou, e o que deve ser corrigido | O cadastro aceitava telefone só com símbolos, como "((((((((". Sugeriu aceitar só números e formatar como (xx) xxxxx-xxxx. Registrado como C-01. |
| Funcionalidade não testada, e por quê | Parte B (profissional e administrador): testou apenas como cliente. |
| Evidências (prints) | Sem prints. |

### 4.2 Colega 2

| Campo | Resposta |
|---|---|
| Nome | Theo Nicoleli |
| Data do teste e dispositivo | 29/10/2026 · iPhone |
| O que testou e funcionou | A1 a A8, A12, A14 e A15 OK. "Tudo que testei funcionou." |
| O que testou e não funcionou, e o que deve ser corrigido | Nenhuma falha. Sugestão: simplificar o cadastro, usando apenas o número de telefone. |
| Funcionalidade não testada, e por quê | A9, A10, A11 e A13 e a Parte B: "queria testar como cliente do barbeiro". |
| Evidências (prints) | Sem prints. |

### 4.3 Colega 3

| Campo | Resposta |
|---|---|
| Nome | Davi Inoue |
| Data do teste e dispositivo | 31/10/2026 · notebook Windows + Chrome |
| O que testou e funcionou | Partes A e B completas (A1 a A15 e B1 a B4): todos OK. "Bem intuitivo e responsivo." |
| O que testou e não funcionou, e o que deve ser corrigido | Nenhuma falha. Sugestões: enviar WhatsApp ou e-mail com os dados do agendamento e integrar com o Google Agenda (a integração com o Google Agenda foi aplicada, ver changelog). |
| Funcionalidade não testada, e por quê | Nenhuma. |
| Evidências (prints) | 1 print enviado pelo Google Forms (pasta do formulário no Google Drive). |

### 4.4 Colega 4

| Campo | Resposta |
|---|---|
| Nome | Arthur Furtado |
| Data do teste e dispositivo | 31/10/2026 · iPhone + Safari |
| O que testou e funcionou | A1 a A12, A14 e A15 OK. "Tudo." |
| O que testou e não funcionou, e o que deve ser corrigido | A13 marcado como Falhou: "Eu consegui acessar com o admin". Registrado como C-02. Sugestão: horários disponíveis em azul e indisponíveis em cinza (aplicada, ver changelog). |
| Funcionalidade não testada, e por quê | Parte B: "não recebi acesso". |
| Evidências (prints) | Sem prints. |

### 4.5 Colega 5

| Campo | Resposta |
|---|---|
| Nome | [PENDENTE: aguardando teste real] |
| Data do teste | [PENDENTE: aguardando teste real] |
| O que testou e funcionou | [PENDENTE: aguardando teste real] |
| O que testou e não funcionou, e o que deve ser corrigido | [PENDENTE: aguardando teste real] |
| Funcionalidade não testada, e por quê | [PENDENTE: aguardando teste real] |
| Evidências (prints) | [PENDENTE: aguardando teste real] |

## 5. Defeitos apontados pelos colegas

| ID | Descrição | Encontrado por | Evidência (`docs/evidencias/colegas/`) | Severidade | Correção aplicada | Status |
|---|---|---|---|---|---|---|
| C-01 | O campo telefone do cadastro aceitava valores sem número algum, como "((((((((" ou "--------", porque a validação só conferia os caracteres permitidos. | Colega 1 (Andrew) | Relato no formulário (passo A3) | Média | O servidor passou a exigir DDD e número (10 ou 11 dígitos, aceitando +55) e grava o telefone sempre no formato (43) 99999-0000; o campo do formulário recusa o valor antes do envio. Testes: `test_telefone_sem_digitos_suficientes_e_recusado`, `test_telefone_valido_e_formatado`. | Corrigido |
| C-02 | Passo A13 marcado como Falhou com o comentário "Eu consegui acessar com o admin". | Colega 4 (Arthur Furtado) | Relato no formulário (passo A13) | — | Não é defeito do sistema. Em conversa, o colega confirmou que viu a tela de login: ele estava sem login, e nesse caso `/admin/` redireciona para o login, como esperado. Logado como cliente, a página responde "Acesso negado" (CT-06, `test_auth_controller.py::test_controle_de_acesso_por_papel`). A causa foi o texto do passo A13, que não dizia que era preciso estar logado; o texto foi corrigido. | Encerrado (não é defeito) |

> Para cada defeito: reproduzir, criar um teste automatizado que falhe, corrigir, rodar `pytest` e registrar a correção no [changelog](changelog-melhorias.md).

## 6. Parecer final

[PENDENTE: aguardando teste real. Preencher depois dos 5 testes e das correções, informando se a versão atende ao critério de aprovação do plano de testes: nenhum defeito Crítico ou Alto aberto.]
