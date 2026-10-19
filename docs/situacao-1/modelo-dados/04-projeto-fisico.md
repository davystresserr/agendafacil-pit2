# Projeto físico — decisões e domínios

O DDL completo está em [`03-projeto-fisico.sql`](03-projeto-fisico.sql). As migrações Alembic (`src/migrations/versions/`) reproduzem esse DDL; a parte específica do PostgreSQL (restrição `EXCLUDE`) só é aplicada quando o banco é PostgreSQL.

## SGBD escolhido

**PostgreSQL 16**: livre, popular e bem suportado pelo Render. Atende à orientação do material ("nada de usar SGBD obscuros"). O SQLite é usado **somente** nos testes automatizados.

## Domínio × tipo de dado

O material lembra que *"um tipo de dado não é o mesmo que o domínio do atributo"*. Por isso cada domínio é garantido por `CHECK`, `UNIQUE` ou `NOT NULL`, e não só pelo tipo:

| Atributo | Tipo físico | Domínio (regra) | Como é garantido |
|---|---|---|---|
| usuarios.email | VARCHAR(120) | e-mail válido, minúsculo, único | `UNIQUE`, `CHECK` (minúsculo e formato mínimo) + validação no serviço |
| usuarios.papel | VARCHAR(15) | {cliente, profissional, admin} | `CHECK ... IN` |
| servicos.preco | NUMERIC(8,2) | (0; 999.999,99] em reais | `CHECK preco > 0`; NUMERIC evita erro de arredondamento de float |
| servicos.duracao_min | INTEGER | [5; 480] minutos | `CHECK BETWEEN` |
| horarios_disponiveis.dia_semana | SMALLINT | {0..6}, 0 = segunda | `CHECK BETWEEN 0 AND 6` |
| horarios_disponiveis.hora_fim | TIME | maior que hora_inicio | `CHECK hora_fim > hora_inicio` |
| agendamentos.status | VARCHAR(15) | {agendado, cancelado, concluido} | `CHECK ... IN` |
| agendamentos.(inicio, fim) | TIMESTAMP | fim > inicio; sem sobreposição por profissional | `CHECK` + `EXCLUDE USING gist` |
| agendamentos.cancelado_em | TIMESTAMP | preenchido se e somente se status = cancelado | `CHECK` de equivalência |

## Restrição de não sobreposição (RN02)

```sql
EXCLUDE USING gist (
    int4range(profissional_id, profissional_id, '[]') WITH =,
    tsrange(inicio, fim, '[)') WITH &&
) WHERE (status = 'agendado')
```

Lê-se: "não podem existir duas linhas com status `agendado` em que o profissional seja o mesmo **e** os intervalos `[inicio, fim)` se sobreponham". O intervalo é semiaberto, então um atendimento das 10:00 às 10:30 **não** conflita com outro que começa às 10:30. O profissional é convertido em uma faixa de um único valor (`int4range`) para que a restrição use só operadores de faixa nativos do GiST, sem depender da extensão `btree_gist`.

## Integridade referencial

| FK | Ação ON DELETE | Justificativa |
|---|---|---|
| profissionais.usuario_id | CASCADE | Profissional não existe sem o usuário. |
| profissional_servico.* | CASCADE | A associação some junto com qualquer lado. |
| horarios_disponiveis.profissional_id | CASCADE | Composição: a jornada pertence ao profissional. |
| agendamentos.* | RESTRICT | O histórico de agendamentos não pode ser apagado indiretamente. Para "remover" serviços ou profissionais usamos `ativo = false` (exclusão lógica). |

## Índices

| Índice | Consulta atendida |
|---|---|
| ix_ag_profissional_inicio | Horários livres e agenda do profissional por dia |
| ix_ag_cliente_inicio | "Meus agendamentos" |
| ix_ag_servico | Junções e relatórios por serviço |
| ix_ps_servico | "Quais profissionais realizam o serviço X?" |
| uq_ag_profissional_inicio_ativo (parcial) | Segunda barreira contra agendamento duplo, portável para SQLite |
| índice GiST da restrição EXCLUDE | Detecção de sobreposição de intervalos |

## Fuso horário

Os horários são armazenados como `TIMESTAMP` (sem fuso) no horário local do salão (`America/Sao_Paulo`, configurável em `TZ_APP`). A aplicação calcula "agora" nesse fuso, o que evita a confusão de horários quando o servidor (Render) roda em UTC.
