# Diagrama de classes (persistência e serviços)

```mermaid
classDiagram
    direction LR

    class Usuario {
        +int id
        +str nome
        +str email
        +str senha_hash
        +str telefone
        +Papel papel
        +bool ativo
        +datetime criado_em
        +definir_senha(senha)
        +verificar_senha(senha) bool
        +is_admin() bool
    }

    class Papel {
        <<enumeration>>
        cliente
        profissional
        admin
    }

    class Profissional {
        +int id
        +int usuario_id
        +str especialidade
        +str bio
        +str foto_url
        +bool ativo
        +realiza(servico) bool
        +iniciais() str
    }

    class Servico {
        +int id
        +str nome
        +str descricao
        +Decimal preco
        +int duracao_min
        +bool ativo
    }

    class HorarioDisponivel {
        +int id
        +int profissional_id
        +int dia_semana
        +time hora_inicio
        +time hora_fim
        +contem(inicio, fim) bool
    }

    class Agendamento {
        +int id
        +int cliente_id [0..1]
        +str cliente_nome
        +str cliente_telefone
        +str token
        +int profissional_id
        +int servico_id
        +datetime inicio
        +datetime fim
        +StatusAgendamento status
        +str observacao
        +datetime criado_em
        +datetime cancelado_em
        +pode_ser_cancelado_por_cliente(agora) bool
        +nome_do_cliente() str
    }

    class StatusAgendamento {
        <<enumeration>>
        agendado
        cancelado
        concluido
    }

    class AgendamentoService {
        +horarios_do_dia(profissional, servico, data, agora) list
        +horarios_livres(profissional, servico, data, agora) list
        +agendar(cliente, profissional, servico, inicio, agora) Agendamento
        +agendar_sem_conta(nome, telefone, profissional, servico, inicio, agora) Agendamento
        +cancelar(agendamento, usuario, agora)
        +cancelar_pelo_link(agendamento, agora)
        +concluir(agendamento, profissional, agora)
    }

    class AuthService {
        +cadastrar_cliente(nome, email, telefone, senha) Usuario
        +autenticar(email, senha) Usuario
    }

    Usuario "1" -- "0..1" Profissional : é
    Usuario "0..1" -- "0..*" Agendamento : agenda (cliente cadastrado)
    Profissional "1" -- "0..*" Agendamento : atende
    Servico "1" -- "0..*" Agendamento : é prestado em
    Profissional "1" *-- "0..*" HorarioDisponivel : possui
    Profissional "0..*" -- "1..*" Servico : realiza
    Usuario ..> Papel
    Agendamento ..> StatusAgendamento
    AgendamentoService ..> Agendamento : cria/altera
    AgendamentoService ..> HorarioDisponivel : consulta
    AuthService ..> Usuario : cria/autentica
```

**Notas:**

- `Profissional` é uma especialização por associação 1:1 com `Usuario` (o login é sempre um `Usuario`; os dados de trabalho ficam em `Profissional`). Essa escolha evita colunas nulas na tabela de usuários para clientes.
- `HorarioDisponivel` é composição de `Profissional`: se o profissional for removido, sua jornada também é.
- A associação N:N `Profissional`–`Servico` vira a tabela `profissional_servico` no modelo lógico.
- Agendamento sem cadastro (RF15): `cliente_id` fica nulo e o agendamento guarda `cliente_nome`, `cliente_telefone` e um `token` aleatório, que forma o link privado para ver e cancelar (RN08). A restrição `ck_ag_cliente` exige um dos dois casos.
