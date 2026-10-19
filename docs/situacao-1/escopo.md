# Situação 1 — Escopo revisado do AgendaFácil

> **Observação sobre o PIT I:** os documentos originais do PIT I não estavam disponíveis na pasta do projeto. Por isso, o planejamento foi **reconstruído do zero** a partir da ideia original (sistema de agendamento para salões e barbearias) e revisado conforme o material do PIT II (Kaizen / melhoria contínua).

## 1. Descrição do problema

Salões de beleza e barbearias de pequeno porte costumam controlar a agenda em cadernos, planilhas ou mensagens de WhatsApp. Isso gera:

- **conflitos de horário**: dois clientes marcados no mesmo horário com o mesmo profissional;
- **faltas sem aviso**: o cliente desiste e o horário fica ocioso;
- **retrabalho**: o atendente gasta tempo respondendo "tem horário amanhã?";
- **falta de informação**: o cliente não sabe preço nem duração do serviço antes de chegar.

## 2. Objetivos

**Objetivo geral:** oferecer um sistema web simples para o cliente agendar serviços online e para o estabelecimento gerenciar a agenda sem conflitos.

**Objetivos específicos:**

1. Permitir que o cliente veja serviços, preços, durações e horários livres, e agende sem intermediários.
2. Impedir, no sistema e no banco de dados, dois agendamentos sobrepostos para o mesmo profissional.
3. Permitir o cancelamento pelo cliente com antecedência mínima de 2 horas, liberando o horário.
4. Dar ao profissional uma visão da sua agenda e controle dos seus horários de trabalho.
5. Dar ao administrador o cadastro de serviços e profissionais.

## 3. Atores

| Ator | Descrição |
|---|---|
| **Cliente** | Pessoa que se cadastra, consulta serviços e agenda/cancela horários. |
| **Profissional** | Cabeleireiro(a) ou barbeiro(a). Consulta sua agenda, define seus horários disponíveis e marca atendimentos como concluídos. |
| **Administrador** | Dono ou gerente. Cadastra serviços e profissionais e acompanha todos os agendamentos. |

## 4. Escopo

### 4.1 Incluído

- Cadastro e login de usuários com senha criptografada (hash).
- Controle de acesso por papel (cliente, profissional, administrador).
- Catálogo de serviços com preço e duração.
- Cadastro de profissionais e dos serviços que cada um realiza.
- Cadastro dos horários disponíveis (jornada semanal) de cada profissional.
- Agendamento: escolher serviço → profissional → data → horário livre → confirmar.
- Listagem "Meus agendamentos" e cancelamento com regra de 2 horas.
- Painel do profissional (agenda, horários, concluir atendimento).
- Painel do administrador (serviços, profissionais, todos os agendamentos).
- Interface responsiva (celular e computador).
- Páginas de erro 404/500 personalizadas e mensagens de feedback.

### 4.2 Excluído (fora desta versão)

- Pagamento online.
- Notificações por e-mail, SMS ou WhatsApp.
- Aplicativo mobile nativo (a versão web é responsiva).
- Múltiplos estabelecimentos (multiempresa).
- Recuperação de senha por e-mail.
- Programa de fidelidade e avaliações.

## 5. Requisitos funcionais

| ID | Requisito | Ator | Prioridade |
|---|---|---|---|
| RF01 | O sistema deve permitir o cadastro de clientes com nome, e-mail, telefone e senha. | Cliente | Alta |
| RF02 | O sistema deve autenticar usuários por e-mail e senha. | Todos | Alta |
| RF03 | O sistema deve listar os serviços ativos com nome, descrição, preço e duração. | Todos | Alta |
| RF04 | O sistema deve permitir ao cliente agendar um serviço com um profissional em um horário livre. | Cliente | Alta |
| RF05 | O sistema deve exibir apenas horários livres, considerando a jornada do profissional, a duração do serviço e os agendamentos existentes. | Cliente | Alta |
| RF06 | O sistema deve impedir dois agendamentos sobrepostos para o mesmo profissional. | Sistema | Alta |
| RF07 | O sistema deve listar os agendamentos do cliente ("Meus agendamentos"). | Cliente | Alta |
| RF08 | O sistema deve permitir ao cliente cancelar um agendamento com pelo menos 2 horas de antecedência. | Cliente | Alta |
| RF09 | O sistema deve exibir ao profissional sua agenda de atendimentos. | Profissional | Alta |
| RF10 | O sistema deve permitir ao profissional cadastrar e remover seus horários disponíveis. | Profissional | Média |
| RF11 | O sistema deve permitir ao profissional marcar um atendimento como concluído. | Profissional | Média |
| RF12 | O sistema deve permitir ao administrador cadastrar, editar, ativar e desativar serviços. | Administrador | Alta |
| RF13 | O sistema deve permitir ao administrador cadastrar profissionais e os serviços que realizam. | Administrador | Alta |
| RF14 | O sistema deve permitir ao administrador visualizar todos os agendamentos. | Administrador | Média |

## 6. Regras de negócio

| ID | Regra |
|---|---|
| RN01 | Um agendamento ocupa um intervalo `[início, início + duração do serviço)` de um profissional para um serviço. |
| RN02 | Não pode haver dois agendamentos ativos (status `agendado`) sobrepostos para o mesmo profissional. |
| RN03 | O cliente só pode cancelar com pelo menos **2 horas** de antecedência do início. O profissional e o administrador podem cancelar a qualquer momento (ex.: imprevisto do profissional). |
| RN04 | Preço e duração do serviço são obrigatórios e positivos (duração entre 5 e 480 minutos). |
| RN05 | O e-mail do usuário é único. |
| RN06 | Não é possível agendar no passado nem fora da jornada cadastrada do profissional. |
| RN07 | O profissional só pode ser agendado para serviços que ele realiza. |

## 7. Requisitos não funcionais

| ID | Categoria | Requisito |
|---|---|---|
| RNF01 | Desempenho | Páginas principais devem responder em até 2 segundos com até 50 usuários simultâneos. Consultas de horários usam índices por profissional e data. |
| RNF02 | Segurança | Senhas armazenadas apenas como hash (PBKDF2/scrypt via `werkzeug.security`). |
| RNF03 | Segurança | Controle de acesso por papel em todas as rotas restritas; formulários protegidos contra CSRF; cookies de sessão `HttpOnly` e `Secure` em produção. |
| RNF04 | Segurança | Validação de entrada no servidor (sempre) e no cliente (HTML5 + JavaScript). Consultas parametrizadas via ORM (sem SQL concatenado). |
| RNF05 | Usabilidade | Agendar um horário em no máximo 4 passos; mensagens claras de erro e sucesso; layout responsivo a partir de 360 px. |
| RNF06 | Usabilidade | Seguir os princípios de IHC do material: clareza, consistência, simplicidade, controle do usuário, recuperação de erros e feedback imediato. |
| RNF07 | Disponibilidade | Hospedagem em nuvem (Render) com HTTPS e domínio via Cloudflare; meta de 99% de disponibilidade mensal. |
| RNF08 | Manutenibilidade | Arquitetura MVC com camada de serviços; cobertura de testes automatizados acima de 70%. |
| RNF09 | Portabilidade | Funcionar nas versões atuais de Chrome, Firefox, Safari e Edge. |
| RNF10 | Integridade | Regras críticas (unicidade de e-mail, valores positivos, não sobreposição) garantidas também por restrições no PostgreSQL. |

## 8. Melhorias em relação ao planejamento original (Kaizen)

- Inclusão da entidade **HorarioDisponivel**, que no plano original não existia: sem ela não era possível calcular horários livres.
- Inclusão da tabela associativa **profissional_servico** (RN07), para que cada profissional ofereça só os serviços que realiza.
- A regra de não sobreposição passou a ser garantida em duas camadas: no serviço (Python) e no banco (restrição `EXCLUDE` com `tsrange` no PostgreSQL).
- Status do agendamento definido como domínio fechado: `agendado`, `cancelado`, `concluido`.
- Requisitos não funcionais reescritos de forma mensurável.
