# Modelo conceitual (DER)

Derivado do diagrama de classes de persistência (`../uml/classes.md`). Notação "pé de galinha" (crow's foot).

```mermaid
erDiagram
    USUARIO ||--o| PROFISSIONAL : "é (0..1)"
    USUARIO ||--o{ AGENDAMENTO : "agenda como cliente"
    PROFISSIONAL ||--o{ AGENDAMENTO : "atende"
    SERVICO ||--o{ AGENDAMENTO : "é prestado em"
    PROFISSIONAL ||--o{ HORARIO_DISPONIVEL : "possui"
    PROFISSIONAL }o--|{ SERVICO : "realiza"

    USUARIO {
        int id PK
        string nome
        string email UK
        string senha_hash
        string telefone
        string papel
        bool ativo
        datetime criado_em
    }
    PROFISSIONAL {
        int id PK
        int usuario_id FK
        string especialidade
        string bio
        bool ativo
    }
    SERVICO {
        int id PK
        string nome UK
        string descricao
        decimal preco
        int duracao_min
        bool ativo
    }
    HORARIO_DISPONIVEL {
        int id PK
        int profissional_id FK
        int dia_semana
        time hora_inicio
        time hora_fim
    }
    AGENDAMENTO {
        int id PK
        int cliente_id FK
        int profissional_id FK
        int servico_id FK
        datetime inicio
        datetime fim
        string status
        string observacao
        datetime criado_em
        datetime cancelado_em
    }
```

## Cardinalidades explicadas

| Relacionamento | Cardinalidade | Leitura |
|---|---|---|
| Usuário — Profissional | 1 : 0..1 | Todo profissional é exatamente um usuário; um usuário pode ou não ser profissional (clientes e admins não são). |
| Usuário (cliente) — Agendamento | 1 : 0..N | Um cliente pode ter vários agendamentos; cada agendamento pertence a exatamente um cliente. |
| Profissional — Agendamento | 1 : 0..N | Um profissional atende vários agendamentos; cada agendamento tem exatamente um profissional. |
| Serviço — Agendamento | 1 : 0..N | Um serviço aparece em vários agendamentos; cada agendamento é de exatamente um serviço. |
| Profissional — HorárioDisponível | 1 : 0..N | Um profissional tem várias faixas de horário na semana; cada faixa pertence a um profissional (dependência de existência). |
| Profissional — Serviço | N : N (0..N : 1..N) | Um profissional realiza um ou mais serviços; um serviço pode ser realizado por vários profissionais. Resolvido pela tabela associativa `profissional_servico`. |
