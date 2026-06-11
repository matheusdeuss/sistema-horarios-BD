/* =====================================================================
   Trabalho Final - Banco de Dados (1/2026)
   Visoes (Views) - SQL Server (T-SQL)
   Cada visao envolve pelo menos 3 tabelas.
   ===================================================================== */
USE GestaoHorarios;
GO

/* V1) VW_GRADE_HORARIOS
   O que faz: visao "pronta para consumo" da grade completa do semestre.
   E a visao usada pela aplicacao web para exibir a grade, evitando
   repetir a juncao de 9 tabelas em cada consulta.
   Tabelas (9): alocacao, disciplina, periodo, curso, professor, usuario,
   horario, dia_semana, sala. */
CREATE VIEW vw_grade_horarios AS
SELECT a.id_alocacao,
       c.sigla            AS curso,
       p.numero           AS periodo,
       d.codigo           AS cod_disciplina,
       d.nome             AS disciplina,
       u.nome             AS professor,
       ds.abreviacao      AS dia,
       h.slot,
       h.hora_inicio,
       h.hora_fim,
       s.bloco + '-' + s.numero AS sala
FROM alocacao a
JOIN disciplina d  ON d.id_disciplina = a.id_disciplina
JOIN periodo p     ON p.id_periodo    = d.id_periodo
JOIN curso c       ON c.id_curso      = p.id_curso
JOIN professor pr  ON pr.id_professor = a.id_professor
JOIN usuario u     ON u.id_usuario    = pr.id_usuario
JOIN horario h     ON h.id_horario    = a.id_horario
JOIN dia_semana ds ON ds.id_dia       = h.id_dia
JOIN sala s        ON s.id_sala       = a.id_sala;
GO

/* V2) VW_CARGA_PROFESSORES
   O que faz: resume a carga de trabalho de cada professor no semestre:
   quantidade de disciplinas, carga horaria total e total de alunos
   matriculados em suas turmas. Apoia a coordenacao na verificacao do
   equilibrio da distribuicao de carga docente.
   Tabelas (5): professor, usuario, alocacao, disciplina, matricula. */
CREATE VIEW vw_carga_professores AS
SELECT pr.id_professor,
       u.nome                          AS professor,
       pr.titulacao,
       COUNT(DISTINCT d.id_disciplina) AS qtde_disciplinas,
       SUM(d.carga_horaria)            AS carga_horaria_total,
       COUNT(m.id_matricula)           AS total_alunos
FROM professor pr
JOIN usuario u          ON u.id_usuario    = pr.id_usuario
JOIN alocacao a         ON a.id_professor  = pr.id_professor
JOIN disciplina d       ON d.id_disciplina = a.id_disciplina
LEFT JOIN matricula m   ON m.id_alocacao   = a.id_alocacao
GROUP BY pr.id_professor, u.nome, pr.titulacao;
GO

/* Exemplos de uso das visoes */
SELECT * FROM vw_grade_horarios ORDER BY dia, slot, periodo;
SELECT * FROM vw_carga_professores ORDER BY carga_horaria_total DESC;
