# Manual do usuário — AgendaFácil

O AgendaFácil é um sistema web para agendar serviços em salões e barbearias. Funciona no computador e no celular, sem instalar nada: basta abrir o endereço no navegador.

> Os prints citados estão em [`docs/evidencias/`](../evidencias/).

## 1. Perfis de acesso

| Perfil | O que pode fazer |
|---|---|
| **Cliente** | Ver serviços, agendar, ver e cancelar os próprios agendamentos |
| **Profissional** | Ver a própria agenda, concluir ou cancelar atendimentos, cadastrar os horários em que trabalha |
| **Administrador** | Cadastrar e editar serviços, cadastrar profissionais, ver e cancelar qualquer agendamento |

O menu no topo mostra apenas as opções do seu perfil. No celular, toque em **☰** para abrir o menu.

## 2. Cliente

### 2.1 Criar conta
1. Clique em **Criar conta** (canto superior direito).
2. Preencha nome, e-mail, telefone (opcional) e uma senha de pelo menos 8 caracteres, e repita a senha.
3. Clique em **Criar conta**. Você entra automaticamente.

Se o e-mail já estiver cadastrado, o sistema avisa e mantém o que você digitou (print `05-cadastro-email-duplicado.png`).

### 2.2 Entrar e sair
- **Entrar:** informe e-mail e senha. Se algo estiver errado, aparece "E-mail ou senha incorretos."
- **Sair:** clique em **Sair** no menu.

### 2.3 Agendar um horário
1. Na página inicial, escolha o serviço e clique em **Agendar** (ou use **Agendar** no menu).
2. **Passo 2:** escolha o profissional.
3. **Passo 3:** escolha a data. Os horários livres aparecem automaticamente; só são mostrados horários dentro do expediente do profissional, no futuro e que comportam a duração do serviço.
4. Clique no horário desejado (ele fica azul), escreva uma observação se quiser e clique em **Confirmar agendamento**.
5. Você vai para **Meus agendamentos**, com a mensagem de confirmação.

Em qualquer passo, use o link **trocar** para mudar o serviço ou o profissional.

Se outra pessoa reservar o mesmo horário segundos antes de você, aparece "Este horário acabou de ser ocupado. Escolha outro horário." e a lista é atualizada (print `12-horario-ocupado.png`).

### 2.4 Ver e cancelar agendamentos
1. Clique em **Meus agendamentos**.
2. Cada agendamento mostra data/hora, serviço, profissional e status (**Agendado**, **Cancelado** ou **Concluído**).
3. Para cancelar, clique em **Cancelar** e confirme em **Sim, confirmar**. O horário volta a ficar disponível.

**Regra:** o cliente só pode cancelar com **pelo menos 2 horas de antecedência**. Depois desse prazo o botão some e aparece "Cancelamento indisponível (menos de 2h). Fale com o salão."

## 3. Profissional

Ao entrar, você vai direto para **Minha agenda**.

- **Agenda:** lista os atendimentos de hoje em diante, com nome e telefone do cliente e a observação dele.
- **Concluir:** aparece depois que o horário do atendimento começa; marca o atendimento como concluído.
- **Cancelar:** o profissional pode cancelar a qualquer momento (ex.: imprevisto). Confirme na janela que aparece.
- **Meus horários disponíveis:** escolha o dia da semana, a hora de início e a de fim e clique em **Adicionar**. Para remover uma faixa, clique em **Remover**. Faixas sobrepostas no mesmo dia não são aceitas. Remover uma faixa não apaga agendamentos já marcados.

## 4. Administrador

Ao entrar, você vai para o **Painel**, que mostra os indicadores do dia e a lista de serviços.

- **Novo serviço:** informe nome, preço (ex.: `45,00`), duração em minutos (5 a 480) e descrição. Preço e duração são obrigatórios e precisam ser positivos.
- **Editar / Desativar / Ativar:** serviços desativados somem da página inicial, mas o histórico é mantido.
- **Profissionais:** lista os profissionais e tem o formulário de cadastro (nome, e-mail, senha inicial, especialidade e serviços que realiza; ao menos um serviço é obrigatório). Depois, o profissional entra com esse e-mail e senha e cadastra os próprios horários.
- **Agendamentos:** lista todos os agendamentos. O administrador pode cancelar qualquer agendamento ativo.

## 5. Mensagens e erros comuns

| Mensagem | O que fazer |
|---|---|
| "Faça login para continuar." | Entre com sua conta; depois do login você volta para a página que tentou abrir. |
| "Você não tem permissão para acessar esta página." | A página é de outro perfil. Use o menu. |
| "Sua sessão expirou. Recarregue a página e tente novamente." | O formulário ficou aberto por muito tempo ou a sessão mudou. Recarregue a página. |
| "Nenhum horário livre nesta data. Tente outro dia." | Escolha outra data ou outro profissional. |
| Página 404 | O endereço não existe. Clique em **Voltar ao início**. |
| Página 500 | Erro inesperado. Tente de novo em instantes; o erro fica registrado para correção. |

## 6. Usuários de demonstração

No ambiente local, o comando `flask seed` cria estes usuários, com a senha definida na variável `SEED_PASSWORD`:

| E-mail | Perfil |
|---|---|
| admin@agendafacil.com | Administrador |
| carlos@agendafacil.com | Profissional (Barbeiro) |
| ana@agendafacil.com | Profissional (Cabeleireira) |
| cliente@agendafacil.com | Cliente |
