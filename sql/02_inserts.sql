/* =====================================================================
   Trabalho Final - Banco de Dados (1/2026)
   Script de carga de dados de teste - SQL Server (T-SQL)
   ===================================================================== */
USE GestaoHorarios;
GO

/* ------------------- USUARIOS ------------------- */
SET IDENTITY_INSERT usuario ON;
INSERT INTO usuario (id_usuario, nome, email, login, senha, tipo_usuario) VALUES
 (1 , 'Carlos Andrade'      , 'carlos.andrade@pucminas.br' , 'carlos'   , '123456', 'COORDENADOR'),
 (2 , 'Ana Beatriz Souza'   , 'ana.souza@pucminas.br'      , 'ana'      , '123456', 'PROFESSOR'),
 (3 , 'Bruno Lima'          , 'bruno.lima@pucminas.br'     , 'bruno'    , '123456', 'PROFESSOR'),
 (4 , 'Camila Rocha'        , 'camila.rocha@pucminas.br'   , 'camila'   , '123456', 'PROFESSOR'),
 (5 , 'Daniel Ferreira'     , 'daniel.ferreira@pucminas.br', 'daniel'   , '123456', 'PROFESSOR'),
 (6 , 'Elaine Martins'      , 'elaine.martins@pucminas.br' , 'elaine'   , '123456', 'PROFESSOR'),
 (7 , 'Fabio Goncalves'     , 'fabio.goncalves@pucminas.br', 'fabio'    , '123456', 'PROFESSOR'),
 (8 , 'Gabriela Nunes'      , 'gabriela.nunes@pucminas.br' , 'gabriela' , '123456', 'PROFESSOR'),
 (9 , 'Henrique Barbosa'    , 'henrique.barbosa@pucminas.br','henrique' , '123456', 'PROFESSOR'),
 (10, 'Igor Almeida'        , 'igor.almeida@sga.pucminas.br'  , 'igor'   , '123456', 'ALUNO'),
 (11, 'Julia Castro'        , 'julia.castro@sga.pucminas.br'  , 'julia'  , '123456', 'ALUNO'),
 (12, 'Kevin Oliveira'      , 'kevin.oliveira@sga.pucminas.br', 'kevin'  , '123456', 'ALUNO'),
 (13, 'Larissa Mendes'      , 'larissa.mendes@sga.pucminas.br', 'larissa', '123456', 'ALUNO'),
 (14, 'Marcos Vinicius Dias', 'marcos.dias@sga.pucminas.br'   , 'marcos' , '123456', 'ALUNO'),
 (15, 'Natalia Pereira'     , 'natalia.pereira@sga.pucminas.br','natalia', '123456', 'ALUNO');
SET IDENTITY_INSERT usuario OFF;

/* ------------------- CURSO E PERIODOS ------------------- */
SET IDENTITY_INSERT curso ON;
INSERT INTO curso (id_curso, nome, sigla, total_periodos) VALUES
 (1, 'Tecnologia em Analise e Desenvolvimento de Sistemas', 'ADS', 5);
SET IDENTITY_INSERT curso OFF;

SET IDENTITY_INSERT periodo ON;
INSERT INTO periodo (id_periodo, id_curso, numero) VALUES
 (1,1,1),(2,1,2),(3,1,3),(4,1,4),(5,1,5);
SET IDENTITY_INSERT periodo OFF;

/* ------------------- DISCIPLINAS (4 por periodo) ------------------- */
SET IDENTITY_INSERT disciplina ON;
INSERT INTO disciplina (id_disciplina, id_periodo, codigo, nome, carga_horaria) VALUES
 (1 ,1,'ALG1','Algoritmos e Estruturas de Dados I'   ,80),
 (2 ,1,'LOG1','Logica Computacional'                 ,60),
 (3 ,1,'MTD1','Matematica Discreta'                  ,60),
 (4 ,1,'IADS','Introducao a ADS'                     ,40),
 (5 ,2,'ALG2','Algoritmos e Estruturas de Dados II'  ,80),
 (6 ,2,'BD1' ,'Banco de Dados I'                     ,80),
 (7 ,2,'POO1','Programacao Orientada a Objetos'      ,80),
 (8 ,2,'ARC1','Arquitetura de Computadores'          ,60),
 (9 ,3,'BD2' ,'Banco de Dados II'                    ,80),
 (10,3,'WEB1','Desenvolvimento Web'                  ,80),
 (11,3,'ENG1','Engenharia de Software'               ,60),
 (12,3,'SO1' ,'Sistemas Operacionais'                ,60),
 (13,4,'MOB1','Desenvolvimento Mobile'               ,80),
 (14,4,'RED1','Redes de Computadores'                ,60),
 (15,4,'GPR1','Gerencia de Projetos'                 ,40),
 (16,4,'SEG1','Seguranca da Informacao'              ,60),
 (17,5,'IA1' ,'Inteligencia Artificial'              ,80),
 (18,5,'NUV1','Computacao em Nuvem'                  ,60),
 (19,5,'TI1' ,'Trabalho Interdisciplinar'            ,40),
 (20,5,'TOP1','Topicos Especiais em Tecnologia'      ,40);
SET IDENTITY_INSERT disciplina OFF;

/* ------------------- PROFESSORES ------------------- */
SET IDENTITY_INSERT professor ON;
INSERT INTO professor (id_professor, id_usuario, matricula, titulacao, data_admissao) VALUES
 (1,2,'P-1001','Doutora'      ,'2015-02-01'),
 (2,3,'P-1002','Mestre'       ,'2017-08-01'),
 (3,4,'P-1003','Doutora'      ,'2012-02-01'),
 (4,5,'P-1004','Mestre'       ,'2019-02-01'),
 (5,6,'P-1005','Especialista' ,'2020-08-01'),
 (6,7,'P-1006','Doutor'       ,'2010-02-01'),
 (7,8,'P-1007','Mestre'       ,'2018-02-01'),
 (8,9,'P-1008','Doutor'       ,'2014-08-01');
SET IDENTITY_INSERT professor OFF;

/* ------------------- HABILITACOES (professor_disciplina) -------------------
   Define quais disciplinas cada professor PODE ministrar                    */
INSERT INTO professor_disciplina (id_professor, id_disciplina) VALUES
 /* Ana (1): algoritmos e logica            */ (1,1),(1,2),(1,5),
 /* Bruno (2): matematica e arquitetura     */ (2,3),(2,8),(2,12),
 /* Camila (3): banco de dados              */ (3,6),(3,9),(3,17),
 /* Daniel (4): web e mobile                */ (4,10),(4,13),(4,4),
 /* Elaine (5): engenharia e gestao         */ (5,11),(5,15),(5,19),
 /* Fabio (6): redes, seguranca e nuvem     */ (6,14),(6,16),(6,18),
 /* Gabriela (7): POO e topicos             */ (7,7),(7,20),(7,10),
 /* Henrique (8): IA, SO e algoritmos       */ (8,17),(8,12),(8,5),(8,1);

/* ------------------- SEMESTRE LETIVO ------------------- */
SET IDENTITY_INSERT semestre_letivo ON;
INSERT INTO semestre_letivo (id_semestre, ano, semestre, data_inicio, data_fim) VALUES
 (1, 2026, 1, '2026-02-02', '2026-07-04');
SET IDENTITY_INSERT semestre_letivo OFF;

/* ------------------- DIAS DA SEMANA ------------------- */
INSERT INTO dia_semana (id_dia, nome, abreviacao) VALUES
 (1,'Segunda-feira','SEG'),
 (2,'Terca-feira'  ,'TER'),
 (3,'Quarta-feira' ,'QUA'),
 (4,'Quinta-feira' ,'QUI'),
 (5,'Sexta-feira'  ,'SEX');

/* ------------------- HORARIOS (2 slots por dia - turno noite) ------------------- */
SET IDENTITY_INSERT horario ON;
INSERT INTO horario (id_horario, id_dia, slot, hora_inicio, hora_fim) VALUES
 (1 ,1,1,'19:00','20:40'),(2 ,1,2,'20:55','22:35'),
 (3 ,2,1,'19:00','20:40'),(4 ,2,2,'20:55','22:35'),
 (5 ,3,1,'19:00','20:40'),(6 ,3,2,'20:55','22:35'),
 (7 ,4,1,'19:00','20:40'),(8 ,4,2,'20:55','22:35'),
 (9 ,5,1,'19:00','20:40'),(10,5,2,'20:55','22:35');
SET IDENTITY_INSERT horario OFF;

/* ------------------- SALAS ------------------- */
SET IDENTITY_INSERT sala ON;
INSERT INTO sala (id_sala, numero, bloco, capacidade, tipo) VALUES
 (1,'101','B3',50,'Comum'),
 (2,'102','B3',50,'Comum'),
 (3,'201','B3',40,'Comum'),
 (4,'L01','B5',30,'Laboratorio'),
 (5,'L02','B5',30,'Laboratorio'),
 (6,'301','B3',60,'Comum');
SET IDENTITY_INSERT sala OFF;

/* ------------------- ALUNOS ------------------- */
SET IDENTITY_INSERT aluno ON;
INSERT INTO aluno (id_aluno, id_usuario, id_curso, matricula, periodo_atual) VALUES
 (1,10,1,'A-2026001',1),
 (2,11,1,'A-2026002',1),
 (3,12,1,'A-2025010',2),
 (4,13,1,'A-2024021',3),
 (5,14,1,'A-2024022',4),
 (6,15,1,'A-2023035',5);
SET IDENTITY_INSERT aluno OFF;
GO

/* ------------------- ALOCACOES -------------------
   Grade gerada pelo algoritmo de coloracao de grafos (alocador.py).
   Resultado: 20 disciplinas alocadas em 5 slots, paralelismo medio 4.0,
   nenhuma restricao violada. Os ids de horario 1..10 correspondem a
   (SEG..SEX) x (slot 1: 19:00 / slot 2: 20:55).                        */
SET IDENTITY_INSERT alocacao ON;
INSERT INTO alocacao (id_alocacao, id_disciplina, id_professor, id_horario, id_sala, id_semestre) VALUES
 (1,1,8,2,1,1),
 (2,2,1,3,1,1),
 (3,3,2,4,1,1),
 (4,4,4,1,1,1),
 (5,5,1,2,2,1),
 (6,6,3,1,2,1),
 (7,7,7,3,2,1),
 (8,8,2,5,1,1),
 (9,9,3,2,3,1),
 (10,10,4,3,3,1),
 (11,11,5,1,3,1),
 (12,12,8,4,2,1),
 (13,13,4,2,4,1),
 (14,14,6,4,3,1),
 (15,15,5,3,4,1),
 (16,16,6,5,2,1),
 (17,17,3,3,5,1),
 (18,18,6,1,4,1),
 (19,19,5,2,5,1),
 (20,20,7,4,4,1);
SET IDENTITY_INSERT alocacao OFF;
GO

/* ------------------- MATRICULAS -------------------
   Cada aluno matricula-se nas 4 disciplinas do seu periodo atual.      */
SET IDENTITY_INSERT matricula ON;
INSERT INTO matricula (id_matricula, id_aluno, id_alocacao, data_matricula, status) VALUES
 (1,1,1,'2026-01-20','ATIVA'),
 (2,1,2,'2026-01-20','ATIVA'),
 (3,1,3,'2026-01-20','ATIVA'),
 (4,1,4,'2026-01-20','ATIVA'),
 (5,2,1,'2026-01-20','ATIVA'),
 (6,2,2,'2026-01-20','ATIVA'),
 (7,2,3,'2026-01-20','ATIVA'),
 (8,2,4,'2026-01-20','ATIVA'),
 (9,3,5,'2026-01-20','ATIVA'),
 (10,3,6,'2026-01-20','ATIVA'),
 (11,3,7,'2026-01-20','ATIVA'),
 (12,3,8,'2026-01-20','ATIVA'),
 (13,4,9,'2026-01-20','ATIVA'),
 (14,4,10,'2026-01-20','ATIVA'),
 (15,4,11,'2026-01-20','ATIVA'),
 (16,4,12,'2026-01-20','ATIVA'),
 (17,5,13,'2026-01-20','ATIVA'),
 (18,5,14,'2026-01-20','ATIVA'),
 (19,5,15,'2026-01-20','ATIVA'),
 (20,5,16,'2026-01-20','ATIVA'),
 (21,6,17,'2026-01-20','ATIVA'),
 (22,6,18,'2026-01-20','ATIVA'),
 (23,6,19,'2026-01-20','ATIVA'),
 (24,6,20,'2026-01-20','ATIVA');
SET IDENTITY_INSERT matricula OFF;
GO
