-- =============================================================================
-- AgendaFácil — Projeto físico (PostgreSQL 16)
-- As migrações Alembic em src/migrations reproduzem este DDL.
-- =============================================================================

-- Extensão necessária para combinar "=" (inteiro) e "&&" (faixa) na mesma
-- restrição EXCLUDE (não sobreposição de agendamentos).
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- -----------------------------------------------------------------------------
-- usuarios
-- -----------------------------------------------------------------------------
CREATE TABLE usuarios (
    id           SERIAL        PRIMARY KEY,
    nome         VARCHAR(100)  NOT NULL,
    email        VARCHAR(120)  NOT NULL,
    senha_hash   VARCHAR(255)  NOT NULL,
    telefone     VARCHAR(20),
    papel        VARCHAR(15)   NOT NULL DEFAULT 'cliente',
    ativo        BOOLEAN       NOT NULL DEFAULT TRUE,
    criado_em    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_usuarios_email UNIQUE (email),
    CONSTRAINT ck_usuarios_papel CHECK (papel IN ('cliente', 'profissional', 'admin')),
    CONSTRAINT ck_usuarios_nome  CHECK (length(trim(nome)) >= 2),
    CONSTRAINT ck_usuarios_email CHECK (email = lower(email) AND email LIKE '%_@_%._%')
);

-- -----------------------------------------------------------------------------
-- profissionais (1:1 com usuarios)
-- -----------------------------------------------------------------------------
CREATE TABLE profissionais (
    id             SERIAL       PRIMARY KEY,
    usuario_id     INTEGER      NOT NULL,
    especialidade  VARCHAR(80),
    bio            TEXT,
    ativo          BOOLEAN      NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_profissionais_usuario UNIQUE (usuario_id),
    CONSTRAINT fk_profissionais_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuarios (id) ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- servicos
-- -----------------------------------------------------------------------------
CREATE TABLE servicos (
    id           SERIAL         PRIMARY KEY,
    nome         VARCHAR(80)    NOT NULL,
    descricao    TEXT,
    preco        NUMERIC(8, 2)  NOT NULL,
    duracao_min  INTEGER        NOT NULL,
    ativo        BOOLEAN        NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_servicos_nome      UNIQUE (nome),
    CONSTRAINT ck_servicos_preco     CHECK (preco > 0),
    CONSTRAINT ck_servicos_duracao   CHECK (duracao_min BETWEEN 5 AND 480)
);

-- -----------------------------------------------------------------------------
-- profissional_servico (associativa N:N)
-- -----------------------------------------------------------------------------
CREATE TABLE profissional_servico (
    profissional_id  INTEGER NOT NULL,
    servico_id       INTEGER NOT NULL,
    CONSTRAINT pk_profissional_servico PRIMARY KEY (profissional_id, servico_id),
    CONSTRAINT fk_ps_profissional FOREIGN KEY (profissional_id)
        REFERENCES profissionais (id) ON DELETE CASCADE,
    CONSTRAINT fk_ps_servico FOREIGN KEY (servico_id)
        REFERENCES servicos (id) ON DELETE CASCADE
);
CREATE INDEX ix_ps_servico ON profissional_servico (servico_id);

-- -----------------------------------------------------------------------------
-- horarios_disponiveis (jornada semanal do profissional)
-- dia_semana: 0 = segunda ... 6 = domingo (mesma convenção de date.weekday() do Python)
-- -----------------------------------------------------------------------------
CREATE TABLE horarios_disponiveis (
    id               SERIAL    PRIMARY KEY,
    profissional_id  INTEGER   NOT NULL,
    dia_semana       SMALLINT  NOT NULL,
    hora_inicio      TIME      NOT NULL,
    hora_fim         TIME      NOT NULL,
    CONSTRAINT fk_horarios_profissional FOREIGN KEY (profissional_id)
        REFERENCES profissionais (id) ON DELETE CASCADE,
    CONSTRAINT ck_horarios_dia     CHECK (dia_semana BETWEEN 0 AND 6),
    CONSTRAINT ck_horarios_ordem   CHECK (hora_fim > hora_inicio),
    CONSTRAINT uq_horarios_inicio  UNIQUE (profissional_id, dia_semana, hora_inicio)
);

-- -----------------------------------------------------------------------------
-- agendamentos
-- -----------------------------------------------------------------------------
CREATE TABLE agendamentos (
    id               SERIAL        PRIMARY KEY,
    cliente_id       INTEGER       NOT NULL,
    profissional_id  INTEGER       NOT NULL,
    servico_id       INTEGER       NOT NULL,
    inicio           TIMESTAMP     NOT NULL,
    fim              TIMESTAMP     NOT NULL,
    status           VARCHAR(15)   NOT NULL DEFAULT 'agendado',
    observacao       VARCHAR(255),
    criado_em        TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cancelado_em     TIMESTAMP,
    CONSTRAINT fk_ag_cliente      FOREIGN KEY (cliente_id)      REFERENCES usuarios (id)      ON DELETE RESTRICT,
    CONSTRAINT fk_ag_profissional FOREIGN KEY (profissional_id) REFERENCES profissionais (id) ON DELETE RESTRICT,
    CONSTRAINT fk_ag_servico      FOREIGN KEY (servico_id)      REFERENCES servicos (id)      ON DELETE RESTRICT,
    CONSTRAINT ck_ag_status   CHECK (status IN ('agendado', 'cancelado', 'concluido')),
    CONSTRAINT ck_ag_periodo  CHECK (fim > inicio),
    CONSTRAINT ck_ag_cancelado CHECK ((status = 'cancelado') = (cancelado_em IS NOT NULL)),
    -- RN02: nenhum par de agendamentos ATIVOS do mesmo profissional pode se sobrepor.
    CONSTRAINT ex_ag_sem_sobreposicao EXCLUDE USING gist (
        profissional_id WITH =,
        tsrange(inicio, fim, '[)') WITH &&
    ) WHERE (status = 'agendado')
);

-- Índices de apoio às consultas mais frequentes
CREATE INDEX ix_ag_profissional_inicio ON agendamentos (profissional_id, inicio);
CREATE INDEX ix_ag_cliente_inicio      ON agendamentos (cliente_id, inicio);
CREATE INDEX ix_ag_servico             ON agendamentos (servico_id);
-- Segunda proteção (portável, inclusive SQLite): mesmo início para o mesmo profissional ativo.
CREATE UNIQUE INDEX uq_ag_profissional_inicio_ativo
    ON agendamentos (profissional_id, inicio) WHERE status = 'agendado';
