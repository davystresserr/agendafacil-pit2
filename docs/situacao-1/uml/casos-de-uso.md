# Diagrama de casos de uso

O Mermaid não tem um tipo nativo de "casos de uso"; usamos um `flowchart` com atores (retângulos arredondados) e casos de uso (elipses), mantendo a semântica UML (associações, «include» e «extend»).

```mermaid
flowchart LR
    Cliente([👤 Cliente])
    Profissional([👤 Profissional])
    Admin([👤 Administrador])

    subgraph Sistema["AgendaFácil"]
        UC01((Cadastrar-se))
        UC02((Fazer login))
        UC03((Consultar serviços))
        UC04((Agendar horário))
        UC05((Consultar horários livres))
        UC06((Ver meus agendamentos))
        UC07((Cancelar agendamento))
        UC08((Ver agenda))
        UC09((Gerenciar horários disponíveis))
        UC10((Concluir atendimento))
        UC11((Gerenciar serviços))
        UC12((Cadastrar profissional))
        UC13((Ver todos os agendamentos))
    end

    Cliente --- UC01
    Cliente --- UC02
    Cliente --- UC03
    Cliente --- UC04
    Cliente --- UC06
    Cliente --- UC07
    Profissional --- UC02
    Profissional --- UC08
    Profissional --- UC09
    Profissional --- UC10
    Profissional --- UC07
    Admin --- UC02
    Admin --- UC11
    Admin --- UC12
    Admin --- UC13
    Admin --- UC07

    UC04 -. "«include»" .-> UC05
    UC04 -. "«include»" .-> UC02
    UC07 -. "«extend» (≥ 2h antes, se cliente)" .-> UC06
```

## Descrição resumida dos casos de uso

| ID | Caso de uso | Ator(es) | Pré-condição | Pós-condição |
|---|---|---|---|---|
| UC01 | Cadastrar-se | Cliente | E-mail ainda não cadastrado | Usuário com papel `cliente` criado |
| UC02 | Fazer login | Todos | Usuário cadastrado e ativo | Sessão autenticada |
| UC03 | Consultar serviços | Todos | — | Lista de serviços ativos exibida |
| UC04 | Agendar horário | Cliente | Logado; serviço e profissional ativos | Agendamento `agendado` criado |
| UC05 | Consultar horários livres | Cliente | Serviço, profissional e data escolhidos | Lista de horários livres exibida |
| UC06 | Ver meus agendamentos | Cliente | Logado | Lista exibida |
| UC07 | Cancelar agendamento | Cliente, Profissional, Admin | Agendamento `agendado`; cliente: ≥ 2h de antecedência | Status `cancelado`; horário liberado |
| UC08 | Ver agenda | Profissional | Logado como profissional | Agenda exibida |
| UC09 | Gerenciar horários disponíveis | Profissional | Logado como profissional | Jornada atualizada |
| UC10 | Concluir atendimento | Profissional | Agendamento `agendado` já iniciado | Status `concluido` |
| UC11 | Gerenciar serviços | Admin | Logado como admin | Serviço criado/alterado/ativado/desativado |
| UC12 | Cadastrar profissional | Admin | E-mail não cadastrado | Usuário `profissional` + Profissional criados |
| UC13 | Ver todos os agendamentos | Admin | Logado como admin | Lista exibida |
