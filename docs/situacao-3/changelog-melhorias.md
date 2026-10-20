# Changelog e melhorias

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/). Cada correção feita após o teste dos colegas deve citar o ID do defeito no [laudo](laudo-qualidade.md).

## [Não lançado]: correções após os testes dos colegas

[PENDENTE: aguardando teste real]

Modelo de registro:

```
### Corrigido
- C-01 (Colega N): <descrição curta do problema>. <o que foi alterado>. Teste: <nome do teste automatizado>.
### Melhorado
- <sugestão do colega aceita>. <o que foi alterado>.
### Não aplicado
- <sugestão recusada> — motivo: <fora do escopo / conflito com regra de negócio / ...>.
```

## [1.0.0] - 2026-10-19: primeira versão funcional (Situação 2)

### Adicionado
- Cadastro e login com senha em hash, controle de acesso por papel (cliente, profissional, administrador) e proteção CSRF.
- Catálogo de serviços com preço e duração.
- Agendamento em 4 passos com cálculo de horários livres (jornada, duração do serviço e agendamentos existentes).
- "Meus agendamentos" e cancelamento com regra de 2 horas para o cliente.
- Painel do profissional: agenda, concluir/cancelar atendimento e horários disponíveis.
- Painel do administrador: serviços (criar, editar, ativar e desativar), profissionais e todos os agendamentos.
- Páginas 404, 403 e 500 personalizadas, mensagens flash, validação no cliente e no servidor e rollback em exceções.
- Layout responsivo com menu ☰ e tabelas em formato de cartão no celular.
- 87 testes automatizados (unitários, integração, PostgreSQL e E2E com Playwright), com 97% de cobertura.
- Deploy no Render (`render.yaml`, `start.sh`) e documentação do domínio no Cloudflare.

### Corrigido durante a verificação interna (antes da entrega aos colegas)
- D-01: restrição de não sobreposição deixou de depender da extensão `btree_gist`.
- D-02: nomes de índices dos models alinhados ao DDL (`flask db check` limpo).
- D-03: rótulos «include»/«extend» no PNG do diagrama de casos de uso.
- D-04: seletor ambíguo no teste E2E de cancelamento.

### Mudanças em relação ao planejamento original (PIT I, reconstruído)
- Nova entidade `HorarioDisponivel` (jornada semanal), necessária para calcular horários livres.
- Nova tabela associativa `profissional_servico` (cada profissional oferece só os serviços que realiza).
- Não sobreposição garantida também no banco, com `EXCLUDE USING gist`.
- Status do agendamento como domínio fechado: agendado, cancelado, concluido.
