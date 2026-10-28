# Formulário de teste do AgendaFácil (para colegas)

Obrigado por testar! Você não precisa conhecer o sistema: siga o roteiro abaixo e anote o que aconteceu. Seja sincero, porque os erros que você encontrar vão me ajudar a melhorar o sistema.

- **Endereço do sistema:** https://agendafacil-l7je.onrender.com
- **Formulário online (Google Forms):** https://docs.google.com/forms/d/e/1FAIpQLSdCHuDmWIJvqfAmrotsPYw6zXVYmXEVRbMB9U2246BEsTLVqA/viewform
- **Versão em formulário interativo (com espaço para anexar prints):** abra o arquivo [`formulario-colegas.html`](formulario-colegas.html) no navegador, preencha e use **Salvar em PDF**.
- **Como enviar:** me mande o PDF (ou este arquivo preenchido) e os prints.

> Dica: se a primeira página demorar até 1 minuto para abrir, é normal. O servidor gratuito "acorda" no primeiro acesso.

---

## Roteiro de teste (passo a passo)

Marque **OK** se funcionou como descrito, ou **Falhou** e descreva o problema. Se algo der erro, tire um print (Windows: `Win + Shift + S`; Mac: `Cmd + Shift + 4`; celular: botões de print).

### Parte A: como cliente

| # | Faça isto | Você deve ver | OK / Falhou |
|---|---|---|---|
| A1 | Abra o endereço do sistema. | A lista de serviços com preço e duração. | |
| A2 | Clique em **Criar conta**, preencha com seus dados (pode usar um e-mail fictício, como `seunome@teste.com`) e uma senha de 8+ caracteres. Escreva a confirmação de senha **diferente** de propósito. | O aviso "As senhas não conferem" antes de enviar. | |
| A3 | Corrija a confirmação e clique em **Criar conta**. | "Conta criada com sucesso!" e seu nome no topo. | |
| A4 | Clique em **Sair** e entre de novo com uma senha **errada**. | "E-mail ou senha incorretos." | |
| A5 | Entre com a senha certa. | "Olá, {seu nome}!" | |
| A6 | Na página inicial, clique em **Agendar** em um serviço. Escolha um profissional e uma data **de segunda a sábado**. | Botões com os horários livres. | |
| A7 | Escolha um horário, escreva uma observação e clique em **Confirmar agendamento**. | "Agendamento confirmado..." e o agendamento em **Meus agendamentos** como "Agendado". | |
| A8 | Tente agendar **de novo o mesmo horário** com o mesmo profissional. | O horário não deve mais aparecer na lista de livres. | |
| A9 | Escolha um domingo. | "Nenhum horário livre nesta data." | |
| A10 | Em **Meus agendamentos**, clique em **Cancelar** e depois em **Voltar**. | Nada muda. | |
| A11 | Clique em **Cancelar** e depois em **Sim, confirmar**. | "Agendamento cancelado" e status "Cancelado". | |
| A12 | Faça um agendamento para **hoje**, para daqui a menos de 2 horas (se houver horário). | Em **Meus agendamentos** aparece "Cancelamento indisponível (menos de 2h)". | |
| A13 | Digite no navegador o endereço do sistema seguido de `/admin/`. | "Acesso negado". | |
| A14 | Digite o endereço seguido de `/pagina-que-nao-existe`. | "Página não encontrada" com botão para voltar. | |
| A15 | Repita A1, A6 e A7 **no celular**. | Tela ajustada ao celular, menu ☰ funcionando. | |

### Parte B: como profissional e administrador (opcional; peça os acessos ao Davy)

| # | Faça isto | Você deve ver | OK / Falhou |
|---|---|---|---|
| B1 | Entre como profissional. | A agenda com os atendimentos. | |
| B2 | Em **Meus horários disponíveis**, adicione um domingo das 10:00 às 12:00. | "Horário adicionado." | |
| B3 | Entre como administrador e crie um serviço com preço **0**. | Mensagem de erro sobre o preço. | |
| B4 | Crie um serviço válido e veja se ele aparece na página inicial. | O serviço novo listado. | |

---

## Formulário de resultado

**Nome de quem testou:** ______________________________________

**Data do teste:** ____/____/______  **Dispositivo/navegador:** ______________________

### 1. O que testou e funcionou
*(descreva as funcionalidades, por exemplo: "cadastro, login, agendamento A6–A7")*

&nbsp;

&nbsp;

### 2. O que testou e NÃO funcionou, e o que deve ser corrigido
*(para cada problema: número do passo, o que você fez, o que aconteceu, o que esperava e, se possível, o nome do print)*

| Passo | O que aconteceu | O que deveria acontecer / sugestão de correção | Print |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

### 3. Funcionalidade não testada, e por quê
*(ex.: "Parte B, não recebi acesso de administrador" ou "A12, não havia horário hoje")*

&nbsp;

&nbsp;

### 4. Sugestões de melhoria (opcional)

&nbsp;

&nbsp;

### 5. Prints anexados
*(liste os nomes dos arquivos, ex.: `erro-passo-A7.png`)*

&nbsp;
