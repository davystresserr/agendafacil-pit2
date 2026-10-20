# Roteiro do vídeo de apresentação (≈ 5 minutos)

> **Atenção à duração:** o material da Situação 3 pede um vídeo "de até cinco minutos", mas o formulário da entrega e a seção "Problema em Foco" falam em vídeo narrado com "no mínimo 5 min". Para atender aos dois, o roteiro mira **exatamente 5:00**. Confirme com o tutor se houver dúvida.

**Preparação antes de gravar**
- Abrir o sistema publicado e "acordar" o servidor 2 minutos antes (plano gratuito).
- Deixar abertas três abas: (1) cliente deslogado, (2) janela anônima para o segundo cliente, (3) repositório no GitHub.
- Ter logins de profissional e admin à mão (não mostrar a senha na tela).
- Gravar em 1080p com microfone; sugestão: OBS Studio ou o gravador do próprio sistema operacional.
- Preencher a seção "Mudanças após os testes" com o conteúdo real do [changelog](changelog-melhorias.md) antes de gravar.

| Tempo | O que mostrar | O que falar (sugestão) |
|---|---|---|
| **0:00–0:30** | Tela inicial do AgendaFácil. | "Sou Davy Gabriel Stresser Pereira, RGM 36963089. Este é o AgendaFácil, um sistema web de agendamento para salões e barbearias, feito no PIT de Engenharia de Software II com Python/Flask, PostgreSQL e hospedado no Render." |
| **0:30–1:00** | README no GitHub; pastas `docs/situacao-1, 2, 3`; diagrama de classes e DER. | "A documentação do PIT I foi revisada: escopo, UML, IHC, modelo de dados normalizado até a 3FN e dicionário de dados. O código segue MVC com uma camada de serviços para as regras de negócio." |
| **1:00–2:00** | Cadastro de cliente (mostrar aviso "As senhas não conferem"), login, escolha do serviço → profissional → data → horário → confirmar. | "O cliente agenda em quatro passos. O sistema só mostra horários dentro da jornada do profissional, no futuro e que comportam a duração do serviço." |
| **2:00–2:40** | Janela anônima com outro cliente tentando o **mesmo** horário → mensagem "acabou de ser ocupado". | "A regra mais importante: não pode haver dois agendamentos no mesmo horário. Ela é garantida no código e também no banco, com uma restrição EXCLUDE do PostgreSQL." |
| **2:40–3:10** | Meus agendamentos → Cancelar → confirmação → cancelado. Mostrar um agendamento a menos de 2h com o aviso de cancelamento indisponível. | "O cliente pode cancelar com até 2 horas de antecedência; depois disso, o sistema explica por que não pode." |
| **3:10–3:40** | Login como profissional: agenda, concluir, horários disponíveis. Login como admin: criar serviço com preço 0 (erro) e depois válido. | "O profissional controla a agenda e os horários; o administrador cadastra serviços e profissionais, com validação de preço e duração." |
| **3:40–4:30** | **Mudanças após os testes dos colegas:** mostrar, lado a lado, o antes e o depois de cada correção listada no changelog. | [PENDENTE: preencher com as correções reais feitas a partir dos testes dos 5 colegas, citando os IDs C-01, C-02... do laudo] |
| **4:30–5:00** | Terminal com `pytest --cov` (87 testes, 97%) e o laudo de qualidade. Encerramento. | "São 87 testes automatizados, incluindo ponta a ponta com Playwright, e o laudo registra os erros encontrados e as correções. Obrigado!" |

## Mudanças desde a versão inicial (para citar no vídeo)

1. **Planejamento (PIT I → PIT II):** entidade `HorarioDisponivel` e tabela `profissional_servico`; regra de não sobreposição também no banco; requisitos não funcionais mensuráveis.
2. **Verificação interna:** D-01 a D-04 do laudo (restrição sem `btree_gist`, índices alinhados, diagrama corrigido, teste E2E corrigido).
3. **Após os colegas:** [PENDENTE: aguardando teste real]
