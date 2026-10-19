# Dicionário de dados — AgendaFácil

Legenda: **PK** = chave primária, **FK** = chave estrangeira, **UK** = única. "Obrig." = NOT NULL.

## usuarios

Pessoas que acessam o sistema (clientes, profissionais e administradores).

| Coluna | Tipo | Obrig. | Domínio / faixa | Chave | Descrição |
|---|---|---|---|---|---|
| id | SERIAL (INTEGER) | Sim | 1 .. 2³¹−1, automático | PK | Identificador do usuário |
| nome | VARCHAR(100) | Sim | 2 a 100 caracteres (sem contar espaços nas pontas) | | Nome completo |
| email | VARCHAR(120) | Sim | e-mail válido, minúsculo | UK | Login do usuário (RN05) |
| senha_hash | VARCHAR(255) | Sim | hash gerado por `werkzeug.security` | | Senha criptografada; a senha em texto puro nunca é armazenada |
| telefone | VARCHAR(20) | Não | dígitos, espaço, `+`, `(`, `)`, `-`; 8 a 20 caracteres | | Telefone para contato |
| papel | VARCHAR(15) | Sim | {`cliente`, `profissional`, `admin`}; padrão `cliente` | | Perfil de acesso |
| ativo | BOOLEAN | Sim | {true, false}; padrão true | | Usuário inativo não consegue fazer login |
| criado_em | TIMESTAMP | Sim | data/hora; padrão = agora | | Data de cadastro |

## profissionais

Dados de trabalho dos usuários com papel `profissional`.

| Coluna | Tipo | Obrig. | Domínio / faixa | Chave | Descrição |
|---|---|---|---|---|---|
| id | SERIAL | Sim | automático | PK | Identificador do profissional |
| usuario_id | INTEGER | Sim | id existente em `usuarios` | FK, UK | Usuário correspondente (relação 1:1) |
| especialidade | VARCHAR(80) | Não | até 80 caracteres | | Ex.: "Barbeiro", "Cabeleireira" |
| bio | TEXT | Não | texto livre | | Apresentação exibida ao cliente |
| ativo | BOOLEAN | Sim | padrão true | | Profissional inativo não aparece para agendamento |

## servicos

Catálogo de serviços do estabelecimento.

| Coluna | Tipo | Obrig. | Domínio / faixa | Chave | Descrição |
|---|---|---|---|---|---|
| id | SERIAL | Sim | automático | PK | Identificador do serviço |
| nome | VARCHAR(80) | Sim | 2 a 80 caracteres | UK | Nome do serviço (ex.: "Corte masculino") |
| descricao | TEXT | Não | texto livre | | Detalhes do serviço |
| preco | NUMERIC(8,2) | Sim | > 0 e ≤ 999.999,99 (R$) | | Preço em reais (RN04) |
| duracao_min | INTEGER | Sim | 5 a 480 | | Duração em minutos (RN04) |
| ativo | BOOLEAN | Sim | padrão true | | Serviço inativo não aparece no catálogo |

## profissional_servico

Associação N:N: quais serviços cada profissional realiza (RN07).

| Coluna | Tipo | Obrig. | Domínio / faixa | Chave | Descrição |
|---|---|---|---|---|---|
| profissional_id | INTEGER | Sim | id existente em `profissionais` | PK, FK | Profissional |
| servico_id | INTEGER | Sim | id existente em `servicos` | PK, FK | Serviço realizado |

## horarios_disponiveis

Jornada semanal de cada profissional.

| Coluna | Tipo | Obrig. | Domínio / faixa | Chave | Descrição |
|---|---|---|---|---|---|
| id | SERIAL | Sim | automático | PK | Identificador da faixa |
| profissional_id | INTEGER | Sim | id existente em `profissionais` | FK, UK (com dia_semana e hora_inicio) | Dono da jornada |
| dia_semana | SMALLINT | Sim | 0 (segunda) a 6 (domingo) | UK (composta) | Dia da semana |
| hora_inicio | TIME | Sim | 00:00 a 23:59 | UK (composta) | Início do expediente nesse dia |
| hora_fim | TIME | Sim | > hora_inicio | | Fim do expediente nesse dia |

## agendamentos

Reserva de um intervalo de tempo de um profissional para um serviço de um cliente.

| Coluna | Tipo | Obrig. | Domínio / faixa | Chave | Descrição |
|---|---|---|---|---|---|
| id | SERIAL | Sim | automático | PK | Identificador do agendamento |
| cliente_id | INTEGER | Sim | id existente em `usuarios` | FK | Cliente que agendou |
| profissional_id | INTEGER | Sim | id existente em `profissionais` | FK | Profissional que atenderá |
| servico_id | INTEGER | Sim | id existente em `servicos` | FK | Serviço agendado |
| inicio | TIMESTAMP | Sim | data/hora futura no momento do agendamento, dentro da jornada | | Início do atendimento (horário local) |
| fim | TIMESTAMP | Sim | > inicio; = inicio + duração do serviço no momento do agendamento | | Fim do atendimento (fato histórico) |
| status | VARCHAR(15) | Sim | {`agendado`, `cancelado`, `concluido`}; padrão `agendado` | | Situação do agendamento |
| observacao | VARCHAR(255) | Não | até 255 caracteres | | Observação do cliente |
| criado_em | TIMESTAMP | Sim | padrão = agora | | Momento em que foi criado |
| cancelado_em | TIMESTAMP | Não | preenchido se e somente se status = `cancelado` | | Momento do cancelamento |

**Restrições compostas de `agendamentos`:** `EXCLUDE USING gist (profissional_id WITH =, tsrange(inicio, fim) WITH &&) WHERE status = 'agendado'` impede sobreposição (RN02). O índice único parcial `(profissional_id, inicio) WHERE status = 'agendado'` é a mesma proteção em versão portável.
