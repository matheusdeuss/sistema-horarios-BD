/* =====================================================================
   Trabalho Final - Banco de Dados (1/2026)
   Consultas SQL - SQL Server (T-SQL)
   Todas as consultas envolvem, no minimo, 3 tabelas.
   ===================================================================== */
USE GestaoHorarios;
GO

/* =====================================================================
   BLOCO 1 - CONSULTAS DE JUNCAO (2)
   ===================================================================== */

/* J1) GRADE COMPLETA DE HORARIOS
   O que faz: exibe a grade de horarios do semestre 2026/1, mostrando dia,
   horario, periodo, disciplina, professor e sala de cada alocacao.
   Tabelas (8): alocacao, disciplina, periodo, professor, usuario,
   horario, dia_semana, sala. */
SELECT ds.abreviacao      AS dia,
       h.hora_inicio,
       p.numero           AS periodo,
       d.codigo,
       d.nome             AS disciplina,
       u.nome             AS professor,
       s.bloco + '-' + s.numero AS sala
FROM alocacao a
JOIN disciplina d  ON d.id_disciplina = a.id_disciplina
JOIN periodo p     ON p.id_periodo    = d.id_periodo
JOIN professor pr  ON pr.id_professor = a.id_professor
JOIN usuario u     ON u.id_usuario    = pr.id_usuario
JOIN horario h     ON h.id_horario    = a.id_horario
JOIN dia_semana ds ON ds.id_dia       = h.id_dia
JOIN sala s        ON s.id_sala       = a.id_sala
ORDER BY h.id_horario, p.numero;

/* J2) DISCIPLINAS MATRICULADAS POR ALUNO
   O que faz: lista cada aluno, sua matricula e as disciplinas em que esta
   matriculado, com o respectivo professor.
   Tabelas (7): aluno, usuario (aluno), matricula, alocacao, disciplina,
   professor, usuario (professor). */
SELECT ua.nome           AS aluno,
       al.matricula,
       d.codigo,
       d.nome            AS disciplina,
       up.nome           AS professor
FROM aluno al
JOIN usuario ua    ON ua.id_usuario    = al.id_usuario
JOIN matricula m   ON m.id_aluno       = al.id_aluno
JOIN alocacao a    ON a.id_alocacao    = m.id_alocacao
JOIN disciplina d  ON d.id_disciplina  = a.id_disciplina
JOIN professor pr  ON pr.id_professor  = a.id_professor
JOIN usuario up    ON up.id_usuario    = pr.id_usuario
WHERE m.status = 'ATIVA'
ORDER BY ua.nome, d.codigo;

/* =====================================================================
   BLOCO 2 - CONSULTAS DE CONJUNTOS (3)
   ===================================================================== */

/* C1) UNIAO - PESSOAS COM VINCULO ATIVO NO SEMESTRE 2026/1
   O que faz: monta a lista unificada de pessoas envolvidas na grade do
   semestre: professores com alguma alocacao UNIAO alunos com matricula.
   Tabelas (6): usuario, professor, alocacao / usuario, aluno, matricula. */
SELECT u.nome, u.email, 'PROFESSOR' AS vinculo
FROM usuario u
JOIN professor pr ON pr.id_usuario = u.id_usuario
JOIN alocacao a   ON a.id_professor = pr.id_professor
UNION
SELECT u.nome, u.email, 'ALUNO' AS vinculo
FROM usuario u
JOIN aluno al    ON al.id_usuario = u.id_usuario
JOIN matricula m ON m.id_aluno    = al.id_aluno
ORDER BY vinculo, nome;

/* C2) INTERSECAO - PROFESSORES HABILITADOS EM DISCIPLINAS DO 1o OU 2o
   PERIODO QUE FORAM EFETIVAMENTE ALOCADOS NO SEMESTRE
   O que faz: retorna os professores que (a) possuem habilitacao para
   alguma disciplina dos periodos iniciais E (b) estao na grade de 2026/1.
   Tabelas (6): usuario, professor, professor_disciplina, disciplina,
   periodo / alocacao. */
SELECT u.nome, pr.matricula
FROM usuario u
JOIN professor pr            ON pr.id_usuario     = u.id_usuario
JOIN professor_disciplina pd ON pd.id_professor   = pr.id_professor
JOIN disciplina d            ON d.id_disciplina   = pd.id_disciplina
JOIN periodo p               ON p.id_periodo      = d.id_periodo
WHERE p.numero IN (1, 2)
INTERSECT
SELECT u.nome, pr.matricula
FROM usuario u
JOIN professor pr ON pr.id_usuario  = u.id_usuario
JOIN alocacao a   ON a.id_professor = pr.id_professor;

/* C3) DIFERENCA - PROFESSORES HABILITADOS QUE NAO MINISTRAM A DISCIPLINA
   O que faz: para cada disciplina, ha varios professores habilitados, mas
   apenas um a ministra. A consulta lista os pares (professor, disciplina)
   em que o professor e habilitado, EXCETO aqueles efetivamente alocados -
   ou seja, a "capacidade ociosa" de habilitacoes do quadro docente.
   Tabelas (5): usuario, professor, professor_disciplina, disciplina /
   alocacao. */
SELECT u.nome AS professor, d.codigo AS disciplina
FROM usuario u
JOIN professor pr            ON pr.id_usuario   = u.id_usuario
JOIN professor_disciplina pd ON pd.id_professor = pr.id_professor
JOIN disciplina d            ON d.id_disciplina = pd.id_disciplina
EXCEPT
SELECT u.nome, d.codigo
FROM usuario u
JOIN professor pr ON pr.id_usuario    = u.id_usuario
JOIN alocacao a   ON a.id_professor   = pr.id_professor
JOIN disciplina d ON d.id_disciplina  = a.id_disciplina
ORDER BY professor, disciplina;

/* =====================================================================
   BLOCO 3 - CONSULTAS DE AGREGACAO (4)
   ===================================================================== */

/* A1) COUNT + GROUP BY + HAVING - PROFESSORES COM MAIS DE UMA DISCIPLINA
   O que faz: conta quantas disciplinas cada professor ministra em 2026/1
   e exibe apenas os que ministram 2 ou mais (sobrecarga docente).
   Tabelas (4): usuario, professor, alocacao, disciplina. */
SELECT u.nome AS professor,
       COUNT(d.id_disciplina) AS qtde_disciplinas
FROM usuario u
JOIN professor pr ON pr.id_usuario   = u.id_usuario
JOIN alocacao a   ON a.id_professor  = pr.id_professor
JOIN disciplina d ON d.id_disciplina = a.id_disciplina
GROUP BY u.nome
HAVING COUNT(d.id_disciplina) >= 2
ORDER BY qtde_disciplinas DESC;

/* A2) AVG/MIN/MAX + GROUP BY + HAVING - CARGA HORARIA POR PERIODO
   O que faz: calcula a carga horaria media, minima e maxima das
   disciplinas de cada periodo do curso, exibindo somente os periodos com
   media igual ou superior a 60 horas.
   Tabelas (3): curso, periodo, disciplina. */
SELECT c.sigla,
       p.numero               AS periodo,
       AVG(d.carga_horaria)   AS media_ch,
       MIN(d.carga_horaria)   AS menor_ch,
       MAX(d.carga_horaria)   AS maior_ch
FROM curso c
JOIN periodo p    ON p.id_curso   = c.id_curso
JOIN disciplina d ON d.id_periodo = p.id_periodo
GROUP BY c.sigla, p.numero
HAVING AVG(d.carga_horaria) >= 60
ORDER BY p.numero;

/* A3) COUNT + GROUP BY - PARALELISMO DA GRADE
   O que faz: mede o objetivo do trabalho - quantas disciplinas ocorrem em
   paralelo em cada horario da grade de 2026/1.
   Tabelas (3): dia_semana, horario, alocacao. */
SELECT ds.nome        AS dia,
       h.hora_inicio,
       COUNT(a.id_alocacao) AS disciplinas_em_paralelo
FROM dia_semana ds
JOIN horario h  ON h.id_dia     = ds.id_dia
JOIN alocacao a ON a.id_horario = h.id_horario
GROUP BY ds.nome, h.hora_inicio, h.id_horario
ORDER BY disciplinas_em_paralelo DESC;

/* A4) SUM + GROUP BY - CARGA HORARIA TOTAL POR PROFESSOR
   O que faz: soma a carga horaria semestral assumida por cada professor
   alocado, permitindo verificar o equilibrio da distribuicao de carga.
   Tabelas (4): usuario, professor, alocacao, disciplina. */
SELECT u.nome AS professor,
       pr.titulacao,
       SUM(d.carga_horaria) AS carga_total
FROM usuario u
JOIN professor pr ON pr.id_usuario   = u.id_usuario
JOIN alocacao a   ON a.id_professor  = pr.id_professor
JOIN disciplina d ON d.id_disciplina = a.id_disciplina
GROUP BY u.nome, pr.titulacao
ORDER BY carga_total DESC;

/* =====================================================================
   BLOCO 4 - OPERADORES LIKE, BETWEEN e IN (3)
   ===================================================================== */

/* L1) LIKE - DISCIPLINAS DA AREA DE DADOS E SEUS PROFESSORES
   O que faz: localiza disciplinas cujo nome contem 'Dados' e mostra
   periodo e professor responsavel na grade de 2026/1.
   Tabelas (5): disciplina, periodo, alocacao, professor, usuario. */
SELECT d.codigo,
       d.nome    AS disciplina,
       p.numero  AS periodo,
       u.nome    AS professor
FROM disciplina d
JOIN periodo p    ON p.id_periodo    = d.id_periodo
JOIN alocacao a   ON a.id_disciplina = d.id_disciplina
JOIN professor pr ON pr.id_professor = a.id_professor
JOIN usuario u    ON u.id_usuario    = pr.id_usuario
WHERE d.nome LIKE '%Dados%'
ORDER BY p.numero;

/* L2) BETWEEN - PROFESSORES ADMITIDOS ENTRE 2012 E 2018 E SUAS TURMAS
   O que faz: lista os professores admitidos no intervalo e as disciplinas
   que ministram, util para analise do corpo docente intermediario.
   Tabelas (4): usuario, professor, alocacao, disciplina. */
SELECT u.nome  AS professor,
       pr.data_admissao,
       d.codigo,
       d.nome  AS disciplina
FROM usuario u
JOIN professor pr ON pr.id_usuario   = u.id_usuario
JOIN alocacao a   ON a.id_professor  = pr.id_professor
JOIN disciplina d ON d.id_disciplina = a.id_disciplina
WHERE pr.data_admissao BETWEEN '2012-01-01' AND '2018-12-31'
ORDER BY pr.data_admissao;

/* L3) IN - GRADE DE SEGUNDA E SEXTA-FEIRA
   O que faz: filtra a grade apenas para os dias de inicio e fim da
   semana, exibindo horario, disciplina e sala.
   Tabelas (5): dia_semana, horario, alocacao, disciplina, sala. */
SELECT ds.nome   AS dia,
       h.hora_inicio,
       d.nome    AS disciplina,
       s.bloco + '-' + s.numero AS sala
FROM dia_semana ds
JOIN horario h    ON h.id_dia        = ds.id_dia
JOIN alocacao a   ON a.id_horario    = h.id_horario
JOIN disciplina d ON d.id_disciplina = a.id_disciplina
JOIN sala s       ON s.id_sala       = a.id_sala
WHERE ds.abreviacao IN ('SEG', 'SEX')
ORDER BY ds.id_dia, h.hora_inicio;
