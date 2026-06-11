/* =====================================================================
   Trabalho Final - Banco de Dados (1/2026)
   Sistema de Gestao de Horarios de Disciplinas - ADS / PUC Minas
   Script DDL - SQL Server (T-SQL)
   13 tabelas
   ===================================================================== */

IF DB_ID('GestaoHorarios') IS NULL
    CREATE DATABASE GestaoHorarios;
GO
USE GestaoHorarios;
GO

/* ---------------------------------------------------------------
   1. USUARIO - cadastro e autenticacao de usuarios do sistema
   --------------------------------------------------------------- */
CREATE TABLE usuario (
    id_usuario    INT IDENTITY(1,1) NOT NULL,
    nome          VARCHAR(100)      NOT NULL,
    email         VARCHAR(100)      NOT NULL,
    login         VARCHAR(30)       NOT NULL,
    senha         VARCHAR(60)       NOT NULL,
    tipo_usuario  VARCHAR(15)       NOT NULL,  -- COORDENADOR | PROFESSOR | ALUNO
    CONSTRAINT pk_usuario PRIMARY KEY (id_usuario),
    CONSTRAINT uq_usuario_email UNIQUE (email),
    CONSTRAINT uq_usuario_login UNIQUE (login),
    CONSTRAINT ck_usuario_tipo CHECK (tipo_usuario IN ('COORDENADOR','PROFESSOR','ALUNO'))
);

/* ---------------------------------------------------------------
   2. CURSO
   --------------------------------------------------------------- */
CREATE TABLE curso (
    id_curso        INT IDENTITY(1,1) NOT NULL,
    nome            VARCHAR(100)      NOT NULL,
    sigla           VARCHAR(10)       NOT NULL,
    total_periodos  INT               NOT NULL,
    CONSTRAINT pk_curso PRIMARY KEY (id_curso),
    CONSTRAINT uq_curso_sigla UNIQUE (sigla),
    CONSTRAINT ck_curso_total CHECK (total_periodos > 0)
);

/* ---------------------------------------------------------------
   3. PERIODO - periodos (semestres curriculares) de um curso
   --------------------------------------------------------------- */
CREATE TABLE periodo (
    id_periodo  INT IDENTITY(1,1) NOT NULL,
    id_curso    INT               NOT NULL,
    numero      INT               NOT NULL,
    CONSTRAINT pk_periodo PRIMARY KEY (id_periodo),
    CONSTRAINT fk_periodo_curso FOREIGN KEY (id_curso) REFERENCES curso (id_curso),
    CONSTRAINT uq_periodo UNIQUE (id_curso, numero),
    CONSTRAINT ck_periodo_numero CHECK (numero > 0)
);

/* ---------------------------------------------------------------
   4. DISCIPLINA - cada disciplina pertence a um periodo do curso
   --------------------------------------------------------------- */
CREATE TABLE disciplina (
    id_disciplina  INT IDENTITY(1,1) NOT NULL,
    id_periodo     INT               NOT NULL,
    codigo         VARCHAR(10)       NOT NULL,
    nome           VARCHAR(100)      NOT NULL,
    carga_horaria  INT               NOT NULL,
    CONSTRAINT pk_disciplina PRIMARY KEY (id_disciplina),
    CONSTRAINT fk_disciplina_periodo FOREIGN KEY (id_periodo) REFERENCES periodo (id_periodo),
    CONSTRAINT uq_disciplina_codigo UNIQUE (codigo),
    CONSTRAINT ck_disciplina_ch CHECK (carga_horaria > 0)
);

/* ---------------------------------------------------------------
   5. PROFESSOR - especializacao de usuario
   --------------------------------------------------------------- */
CREATE TABLE professor (
    id_professor   INT IDENTITY(1,1) NOT NULL,
    id_usuario     INT               NOT NULL,
    matricula      VARCHAR(15)       NOT NULL,
    titulacao      VARCHAR(30)       NULL,      -- Especialista | Mestre | Doutor
    data_admissao  DATE              NULL,
    CONSTRAINT pk_professor PRIMARY KEY (id_professor),
    CONSTRAINT fk_professor_usuario FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario),
    CONSTRAINT uq_professor_usuario UNIQUE (id_usuario),
    CONSTRAINT uq_professor_matricula UNIQUE (matricula)
);

/* ---------------------------------------------------------------
   6. PROFESSOR_DISCIPLINA - habilitacoes (N:M)
      Disciplinas que cada professor esta apto a ministrar
   --------------------------------------------------------------- */
CREATE TABLE professor_disciplina (
    id_professor   INT NOT NULL,
    id_disciplina  INT NOT NULL,
    CONSTRAINT pk_prof_disc PRIMARY KEY (id_professor, id_disciplina),
    CONSTRAINT fk_pd_professor FOREIGN KEY (id_professor) REFERENCES professor (id_professor),
    CONSTRAINT fk_pd_disciplina FOREIGN KEY (id_disciplina) REFERENCES disciplina (id_disciplina)
);

/* ---------------------------------------------------------------
   7. SEMESTRE_LETIVO - semestre em que a grade e gerada
   --------------------------------------------------------------- */
CREATE TABLE semestre_letivo (
    id_semestre  INT IDENTITY(1,1) NOT NULL,
    ano          INT               NOT NULL,
    semestre     INT               NOT NULL,   -- 1 ou 2
    data_inicio  DATE              NOT NULL,
    data_fim     DATE              NOT NULL,
    CONSTRAINT pk_semestre PRIMARY KEY (id_semestre),
    CONSTRAINT uq_semestre UNIQUE (ano, semestre),
    CONSTRAINT ck_semestre CHECK (semestre IN (1,2))
);

/* ---------------------------------------------------------------
   8. DIA_SEMANA
   --------------------------------------------------------------- */
CREATE TABLE dia_semana (
    id_dia      INT          NOT NULL,
    nome        VARCHAR(15)  NOT NULL,
    abreviacao  CHAR(3)      NOT NULL,
    CONSTRAINT pk_dia PRIMARY KEY (id_dia),
    CONSTRAINT uq_dia_nome UNIQUE (nome)
);

/* ---------------------------------------------------------------
   9. HORARIO - 2 slots de alocacao por dia
   --------------------------------------------------------------- */
CREATE TABLE horario (
    id_horario   INT IDENTITY(1,1) NOT NULL,
    id_dia       INT               NOT NULL,
    slot         INT               NOT NULL,   -- 1 ou 2
    hora_inicio  TIME              NOT NULL,
    hora_fim     TIME              NOT NULL,
    CONSTRAINT pk_horario PRIMARY KEY (id_horario),
    CONSTRAINT fk_horario_dia FOREIGN KEY (id_dia) REFERENCES dia_semana (id_dia),
    CONSTRAINT uq_horario UNIQUE (id_dia, slot),
    CONSTRAINT ck_horario_slot CHECK (slot IN (1,2))
);

/* ---------------------------------------------------------------
   10. SALA
   --------------------------------------------------------------- */
CREATE TABLE sala (
    id_sala     INT IDENTITY(1,1) NOT NULL,
    numero      VARCHAR(10)       NOT NULL,
    bloco       VARCHAR(10)       NOT NULL,
    capacidade  INT               NOT NULL,
    tipo        VARCHAR(20)       NOT NULL,    -- Comum | Laboratorio
    CONSTRAINT pk_sala PRIMARY KEY (id_sala),
    CONSTRAINT uq_sala UNIQUE (numero, bloco),
    CONSTRAINT ck_sala_cap CHECK (capacidade > 0)
);

/* ---------------------------------------------------------------
   11. ALUNO - especializacao de usuario
   --------------------------------------------------------------- */
CREATE TABLE aluno (
    id_aluno        INT IDENTITY(1,1) NOT NULL,
    id_usuario      INT               NOT NULL,
    id_curso        INT               NOT NULL,
    matricula       VARCHAR(15)       NOT NULL,
    periodo_atual   INT               NOT NULL,
    CONSTRAINT pk_aluno PRIMARY KEY (id_aluno),
    CONSTRAINT fk_aluno_usuario FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario),
    CONSTRAINT fk_aluno_curso FOREIGN KEY (id_curso) REFERENCES curso (id_curso),
    CONSTRAINT uq_aluno_usuario UNIQUE (id_usuario),
    CONSTRAINT uq_aluno_matricula UNIQUE (matricula)
);

/* ---------------------------------------------------------------
   12. ALOCACAO - nucleo do sistema: disciplina + professor +
       horario + sala em um semestre letivo
   --------------------------------------------------------------- */
CREATE TABLE alocacao (
    id_alocacao    INT IDENTITY(1,1) NOT NULL,
    id_disciplina  INT               NOT NULL,
    id_professor   INT               NOT NULL,
    id_horario     INT               NOT NULL,
    id_sala        INT               NOT NULL,
    id_semestre    INT               NOT NULL,
    data_criacao   DATETIME          NOT NULL DEFAULT GETDATE(),
    CONSTRAINT pk_alocacao PRIMARY KEY (id_alocacao),
    CONSTRAINT fk_aloc_disciplina FOREIGN KEY (id_disciplina) REFERENCES disciplina (id_disciplina),
    CONSTRAINT fk_aloc_professor  FOREIGN KEY (id_professor)  REFERENCES professor (id_professor),
    CONSTRAINT fk_aloc_horario    FOREIGN KEY (id_horario)    REFERENCES horario (id_horario),
    CONSTRAINT fk_aloc_sala       FOREIGN KEY (id_sala)       REFERENCES sala (id_sala),
    CONSTRAINT fk_aloc_semestre   FOREIGN KEY (id_semestre)   REFERENCES semestre_letivo (id_semestre),
    /* uma disciplina e ministrada por apenas um professor (uma unica alocacao por semestre) */
    CONSTRAINT uq_aloc_disciplina UNIQUE (id_disciplina, id_semestre),
    /* um professor nao pode estar em dois lugares no mesmo horario */
    CONSTRAINT uq_aloc_professor  UNIQUE (id_professor, id_horario, id_semestre),
    /* uma sala nao pode receber duas turmas no mesmo horario */
    CONSTRAINT uq_aloc_sala       UNIQUE (id_sala, id_horario, id_semestre)
);

/* ---------------------------------------------------------------
   13. MATRICULA - matricula de alunos nas turmas alocadas
   --------------------------------------------------------------- */
CREATE TABLE matricula (
    id_matricula    INT IDENTITY(1,1) NOT NULL,
    id_aluno        INT               NOT NULL,
    id_alocacao     INT               NOT NULL,
    data_matricula  DATE              NOT NULL DEFAULT GETDATE(),
    status          VARCHAR(12)       NOT NULL DEFAULT 'ATIVA',
    CONSTRAINT pk_matricula PRIMARY KEY (id_matricula),
    CONSTRAINT fk_mat_aluno    FOREIGN KEY (id_aluno)    REFERENCES aluno (id_aluno),
    CONSTRAINT fk_mat_alocacao FOREIGN KEY (id_alocacao) REFERENCES alocacao (id_alocacao),
    CONSTRAINT uq_matricula UNIQUE (id_aluno, id_alocacao),
    CONSTRAINT ck_mat_status CHECK (status IN ('ATIVA','TRANCADA','CANCELADA'))
);
GO

/* =====================================================================
   TRIGGERS - regras de negocio implementadas no SGBD
   ===================================================================== */

/* RN1: disciplinas do MESMO PERIODO nao podem ser alocadas no MESMO HORARIO */
CREATE TRIGGER trg_valida_periodo_horario
ON alocacao
AFTER INSERT, UPDATE
AS
BEGIN
    IF EXISTS (
        SELECT 1
        FROM inserted i
        JOIN disciplina di ON di.id_disciplina = i.id_disciplina
        JOIN alocacao a    ON a.id_horario  = i.id_horario
                          AND a.id_semestre = i.id_semestre
                          AND a.id_alocacao <> i.id_alocacao
        JOIN disciplina da ON da.id_disciplina = a.id_disciplina
        WHERE da.id_periodo = di.id_periodo
    )
    BEGIN
        RAISERROR ('Conflito: ja existe disciplina do mesmo periodo alocada neste horario.', 16, 1);
        ROLLBACK TRANSACTION;
    END
END;
GO

/* RN2: o professor alocado deve estar habilitado para a disciplina */
CREATE TRIGGER trg_valida_habilitacao
ON alocacao
AFTER INSERT, UPDATE
AS
BEGIN
    IF EXISTS (
        SELECT 1
        FROM inserted i
        WHERE NOT EXISTS (
            SELECT 1 FROM professor_disciplina pd
            WHERE pd.id_professor = i.id_professor
              AND pd.id_disciplina = i.id_disciplina
        )
    )
    BEGIN
        RAISERROR ('Professor nao esta habilitado a ministrar esta disciplina.', 16, 1);
        ROLLBACK TRANSACTION;
    END
END;
GO
