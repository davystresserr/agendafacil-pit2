# Roteiro do vídeo de apresentação (≈ 5 minutos)

> **Atenção à duração:** o material da Situação 3 pede um vídeo "de até cinco minutos", mas o formulário da entrega e a seção "Problema em Foco" falam em vídeo narrado com "no mínimo 5 min". Para atender aos dois, o roteiro mira **exatamente 5:00**. Confirme com o tutor se houver dúvida.
>
> **Foco do vídeo:** o enunciado pede para "apresentar as modificações realizadas no sistema" depois dos testes. Por isso, metade do tempo (1:00–3:40) mostra as mudanças, citando o colega que sugeriu cada uma.

**Preparação antes de gravar**
- Abrir https://agendafacil-wine.vercel.app no navegador e, se possível, também no celular (ou no modo celular do navegador, F12).
- Deixar abertas: (1) o site sem login, (2) uma janela anônima para o segundo cliente, (3) o repositório no GitHub, (4) o laudo `docs/situacao-3/laudo-qualidade.md`.
- Ter os logins de profissional e admin à mão (não mostrar a senha na tela).
- Gravar em 1080p com microfone; sugestão: OBS Studio ou o gravador do próprio sistema operacional.

| Tempo | O que mostrar | O que falar (sugestão) |
|---|---|---|
| **0:00–0:30** | Página inicial do AgendaFácil (visual de barbearia). | "Sou Davy Gabriel Stresser Pereira, RGM 36963089. Este é o AgendaFácil, um sistema web de agendamento para salões e barbearias, feito no PIT de Engenharia de Software II com Python e Flask, banco PostgreSQL no Neon e hospedagem na Vercel." |
| **0:30–1:00** | README no GitHub; pastas `docs/situacao-1, 2, 3`; diagrama de classes. | "A documentação do PIT I foi revisada: escopo, UML, IHC, modelo de dados até a 3FN e dicionário de dados. O sistema foi testado por cinco colegas, e o laudo registra o que eles encontraram e o que eu mudei." |
| **1:00–1:40** | **Agendamento sem cadastro (Theo):** Agendar → quadro do serviço com foto → profissional com foto → calendário → horário → nome e celular → página "Seu agendamento" com link privado. | "O Theo sugeriu agendar só com o telefone. Agora o cliente não precisa criar conta: informa nome e celular e recebe um link privado para ver e cancelar. No mesmo celular, o agendamento aparece em Meus agendamentos." |
| **1:40–2:10** | **Telefone (Andrew, C-01):** no cadastro, digitar "((((((((" → erro; digitar 43999991111 → aceito e mostrado como (43) 99999-1111. | "O Andrew encontrou um defeito: o telefone aceitava só símbolos. Agora o sistema exige DDD e número e formata sozinho. Criei um teste automatizado para esse caso." |
| **2:10–2:35** | **Horários (Arthur):** no calendário, escolher um dia com horário ocupado → ocupado em cinza riscado, livres destacados, legenda. | "O Arthur sugeriu diferenciar horários livres e ocupados. Os ocupados agora aparecem em cinza e riscados, e não podem ser escolhidos." |
| **2:35–2:55** | **C-02 (Arthur):** mostrar `/admin/` sem login (vai para o login) e logado como cliente ("Acesso negado"). | "O Arthur marcou que acessou o admin. Investiguei: era a tela de login, não uma falha. O painel só abre com a senha do administrador. Corrigi o texto do roteiro de teste, que induzia a esse engano." |
| **2:55–3:15** | **Google Agenda (Davi):** Meus agendamentos → "Adicionar ao Google Agenda" → evento preenchido. | "O Davi sugeriu levar o agendamento para o Google Agenda. Agora um botão abre o evento já preenchido. A sugestão de aviso por WhatsApp ficou registrada como fora do escopo, porque exige um serviço pago." |
| **3:15–3:40** | **Visual e hospedagem:** página inicial no celular; calendário do mês. | "Também refiz o visual com cara de barbearia, com fotos dos serviços e dos profissionais e um calendário do mês. E troquei a hospedagem para a Vercel com o banco no Neon: o site abre na hora, sem a tela de espera do plano gratuito anterior." |
| **3:40–4:10** | **Regra principal:** janela anônima com outro cliente tentando o **mesmo** horário → "acabou de ser ocupado". | "A regra mais importante continua garantida: não pode haver dois agendamentos no mesmo horário. Ela é verificada no código e também no banco, com uma restrição EXCLUDE do PostgreSQL." |
| **4:10–4:35** | Login como profissional (agenda, concluir) e como admin (serviço com preço 0 dá erro; cadastro de profissional com foto). | "O profissional controla a agenda e os horários; o administrador cadastra serviços e profissionais, agora com foto." |
| **4:35–5:00** | Terminal com `pytest --cov` (116 testes, 97%) e o parecer final do laudo. Encerramento. | "São 116 testes automatizados, incluindo ponta a ponta com Playwright. Os cinco colegas testaram, o único defeito foi corrigido e quatro das seis sugestões foram aplicadas. Obrigado!" |

## Mudanças desde a versão inicial (para citar no vídeo)

1. **Planejamento (PIT I → PIT II):** entidade `HorarioDisponivel` e tabela `profissional_servico`; regra de não sobreposição também no banco; requisitos não funcionais mensuráveis.
2. **Verificação interna:** D-01 a D-04 do laudo (restrição sem `btree_gist`, índices alinhados, diagrama corrigido, teste E2E corrigido).
3. **Após os colegas** (detalhes no [changelog](changelog-melhorias.md) e no [laudo](laudo-qualidade.md)):
   - C-01 (Andrew): telefone exige DDD e número e é salvo formatado.
   - C-02 (Arthur): relato esclarecido, não era defeito; texto do passo A13 corrigido.
   - Sugestões aplicadas: agendamento sem cadastro (Theo), cores dos horários (Arthur), Google Agenda (Davi), telefone formatado (Andrew).
   - Sugestões não aplicadas, com motivo: aviso por WhatsApp ou e-mail (serviço pago) e login próprio de profissional (contraria RF13).
4. **Outras melhorias:** visual de barbearia, fotos de serviços e profissionais, calendário do mês, remoção do campo "observação" da tela, hospedagem na Vercel com banco no Neon.
