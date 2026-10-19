# Modelo lógico normalizado (até a 3FN)

## Esquemas de relação

Notação: **sublinhado = PK**, *itálico = FK*.

- **usuarios** (<u>id</u>, nome, email, senha_hash, telefone, papel, ativo, criado_em)
- **profissionais** (<u>id</u>, *usuario_id* → usuarios.id, especialidade, bio, ativo)
- **servicos** (<u>id</u>, nome, descricao, preco, duracao_min, ativo)
- **profissional_servico** (<u>*profissional_id*</u> → profissionais.id, <u>*servico_id*</u> → servicos.id)
- **horarios_disponiveis** (<u>id</u>, *profissional_id* → profissionais.id, dia_semana, hora_inicio, hora_fim)
- **agendamentos** (<u>id</u>, *cliente_id* → usuarios.id, *profissional_id* → profissionais.id, *servico_id* → servicos.id, inicio, fim, status, observacao, criado_em, cancelado_em)

Chaves candidatas alternativas (viram `UNIQUE`): `usuarios.email`, `profissionais.usuario_id`, `servicos.nome`, `horarios_disponiveis(profissional_id, dia_semana, hora_inicio)`.

## Processo de normalização

### Ponto de partida (não normalizado)

Uma "ficha de agendamento" em planilha, como os salões usam hoje:

| cliente | email_cliente | telefone | profissional | serviços_do_profissional | serviço | preço | duração | data_hora |
|---|---|---|---|---|---|---|---|---|
| Ana | ana@x.com | 4399... | Carlos | Corte, Barba | Corte | 45,00 | 30 | 20/10 14:00 |

### 1FN — atributos atômicos, sem grupos repetitivos

- `serviços_do_profissional` é multivalorado ("Corte, Barba") → sai para a relação **profissional_servico** (uma linha por par profissional/serviço).
- `data_hora` foi decomposto em `inicio` e `fim` (timestamps atômicos). A jornada semanal, que o salão anotava como "seg a sex 9h–18h", vira linhas em **horarios_disponiveis** (um dia por linha).
- Toda relação ganhou chave primária (`id` substituto).

### 2FN — sem dependência parcial da chave

Só há chave composta em `profissional_servico (profissional_id, servico_id)`, que não tem atributos não chave; logo está trivialmente em 2FN. Nas demais tabelas a PK é simples (`id`), então não pode existir dependência parcial.

Na planilha, porém, `preço` e `duração` dependiam só do serviço, e `email_cliente`/`telefone` só do cliente, e não do agendamento inteiro. Por isso esses atributos foram para **servicos** e **usuarios**.

### 3FN — sem dependência transitiva

- Em `agendamentos`, `preco` e `duracao` dependeriam de `servico_id` (agendamento → serviço → preço). Esses campos **não** ficam em `agendamentos`; são obtidos por junção com `servicos`.
- O nome e o telefone do cliente dependeriam de `cliente_id` → ficam apenas em `usuarios`.
- O nome do profissional fica em `usuarios` (via `profissionais.usuario_id`), e não duplicado em `profissionais`.

**Exceção controlada — coluna `fim`:** `fim` poderia ser calculado (`inicio + servicos.duracao_min`). Ela é mantida **de propósito** por dois motivos: (1) se o administrador alterar a duração de um serviço, agendamentos já marcados não podem mudar de tamanho, então `fim` registra um **fato histórico** do momento do agendamento, e não um valor derivado do estado atual; (2) permite a restrição `EXCLUDE ... tsrange(inicio, fim)` no banco, que impede sobreposição de forma atômica. Logo, `fim` depende funcionalmente da chave do agendamento, e não de `servico_id`, e a relação permanece em 3FN.

Pelo mesmo raciocínio, se no futuro houver descontos, o preço cobrado deverá ser gravado no agendamento como fato histórico (fora do escopo atual).

## Dependências funcionais finais

| Relação | Dependências funcionais |
|---|---|
| usuarios | id → nome, email, senha_hash, telefone, papel, ativo, criado_em; email → id |
| profissionais | id → usuario_id, especialidade, bio, ativo; usuario_id → id |
| servicos | id → nome, descricao, preco, duracao_min, ativo; nome → id |
| profissional_servico | (profissional_id, servico_id) → ∅ |
| horarios_disponiveis | id → profissional_id, dia_semana, hora_inicio, hora_fim; (profissional_id, dia_semana, hora_inicio) → id |
| agendamentos | id → cliente_id, profissional_id, servico_id, inicio, fim, status, observacao, criado_em, cancelado_em |

Todo determinante é chave candidata, portanto as relações também atendem à FNBC.
