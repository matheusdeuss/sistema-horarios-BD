# -*- coding: utf-8 -*-
"""Verificacao offline da aplicacao (sem SQL Server):
1. compila app.py / db.py / alocador.py;
2. executa TODAS as instrucoes SQL usadas em app.py contra um banco
   SQLite com o mesmo esquema, dados e visoes;
3. renderiza todos os templates Jinja2 com dados reais."""
import py_compile
import re
import sqlite3
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from teste_consultas import SCHEMA_SQLITE, carrega_inserts  # noqa: E402

print('--- 1. Compilacao ---')
for f in ['app.py', 'db.py', 'alocador.py']:
    py_compile.compile(os.path.join(BASE, f), doraise=True)
    print(f'OK {f}')

print('\n--- 2. SQL da aplicacao ---')
conn = sqlite3.connect(':memory:')
conn.executescript(SCHEMA_SQLITE)
carrega_inserts(conn)
conn.executescript("""
CREATE VIEW vw_grade_horarios AS
SELECT a.id_alocacao, c.sigla AS curso, p.numero AS periodo,
       d.codigo AS cod_disciplina, d.nome AS disciplina, u.nome AS professor,
       ds.abreviacao AS dia, h.slot, h.hora_inicio, h.hora_fim,
       s.bloco || '-' || s.numero AS sala
FROM alocacao a
JOIN disciplina d  ON d.id_disciplina = a.id_disciplina
JOIN periodo p     ON p.id_periodo    = d.id_periodo
JOIN curso c       ON c.id_curso      = p.id_curso
JOIN professor pr  ON pr.id_professor = a.id_professor
JOIN usuario u     ON u.id_usuario    = pr.id_usuario
JOIN horario h     ON h.id_horario    = a.id_horario
JOIN dia_semana ds ON ds.id_dia       = h.id_dia
JOIN sala s        ON s.id_sala       = a.id_sala;
CREATE VIEW vw_carga_professores AS
SELECT pr.id_professor, u.nome AS professor, pr.titulacao,
       COUNT(DISTINCT d.id_disciplina) AS qtde_disciplinas,
       SUM(d.carga_horaria) AS carga_horaria_total,
       COUNT(m.id_matricula) AS total_alunos
FROM professor pr
JOIN usuario u        ON u.id_usuario    = pr.id_usuario
JOIN alocacao a       ON a.id_professor  = pr.id_professor
JOIN disciplina d     ON d.id_disciplina = a.id_disciplina
LEFT JOIN matricula m ON m.id_alocacao   = a.id_alocacao
GROUP BY pr.id_professor, u.nome, pr.titulacao;
""")

sqls = [
    ("login", 'SELECT id_usuario, nome, tipo_usuario FROM usuario WHERE login = ? AND senha = ?', ('carlos', '123456')),
    ("usuarios.dup", 'SELECT 1 AS x FROM usuario WHERE login = ? OR email = ?', ('carlos', 'x@y.z')),
    ("usuarios.insert", 'INSERT INTO usuario (nome, email, login, senha, tipo_usuario) VALUES (?,?,?,?,?)',
     ('Teste Silva', 'teste@pucminas.br', 'teste', '123456', 'ALUNO')),
    ("usuarios.lista", 'SELECT id_usuario, nome, email, login, tipo_usuario FROM usuario ORDER BY nome', ()),
    ("hab.existe", 'SELECT 1 AS x FROM professor_disciplina WHERE id_professor = ? AND id_disciplina = ?', (1, 1)),
    ("hab.insert", 'INSERT INTO professor_disciplina (id_professor, id_disciplina) VALUES (?,?)', (1, 3)),
    ("hab.profs", 'SELECT pr.id_professor, u.nome FROM professor pr JOIN usuario u ON u.id_usuario = pr.id_usuario ORDER BY u.nome', ()),
    ("hab.disc", 'SELECT d.id_disciplina, d.codigo, d.nome, p.numero AS periodo FROM disciplina d JOIN periodo p ON p.id_periodo = d.id_periodo ORDER BY p.numero, d.codigo', ()),
    ("hab.lista", 'SELECT u.nome AS professor, d.codigo, d.nome AS disciplina, pd.id_professor, pd.id_disciplina FROM professor_disciplina pd JOIN professor pr ON pr.id_professor = pd.id_professor JOIN usuario u ON u.id_usuario = pr.id_usuario JOIN disciplina d ON d.id_disciplina = pd.id_disciplina ORDER BY u.nome, d.codigo', ()),
    ("hab.delete", 'DELETE FROM professor_disciplina WHERE id_professor = ? AND id_disciplina = ?', (1, 3)),
    ("grade.view", 'SELECT * FROM vw_grade_horarios ORDER BY dia, slot, periodo', ()),
    ("gerar.disc", 'SELECT id_disciplina AS id, nome, id_periodo FROM disciplina', ()),
    ("gerar.pares", 'SELECT id_professor, id_disciplina FROM professor_disciplina', ()),
    ("gerar.salas", 'SELECT id_sala FROM sala', ()),
    ("gerar.delmat", 'DELETE FROM matricula WHERE id_alocacao IN (SELECT id_alocacao FROM alocacao WHERE id_semestre = ?)', (99,)),
    ("gerar.delaloc", 'DELETE FROM alocacao WHERE id_semestre = ?', (99,)),
    ("rel.view", 'SELECT * FROM vw_carga_professores ORDER BY carga_horaria_total DESC', ()),
]
for nome, sql, params in sqls:
    cur = conn.execute(sql, params)
    n = len(cur.fetchall()) if sql.strip().upper().startswith('SELECT') else cur.rowcount
    print(f'OK {nome:15s} -> {n}')
conn.rollback()

print('\n--- 3. Renderizacao dos templates ---')
import jinja2  # noqa: E402

env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(BASE, 'templates')))


def url_for(endpoint, **kw):
    return '/' + endpoint


def get_flashed_messages(with_categories=False):
    return [('ok', 'Mensagem de teste')] if with_categories else ['Mensagem de teste']


ctx_global = {
    'url_for': url_for,
    'get_flashed_messages': get_flashed_messages,
    'session': {'id_usuario': 1, 'nome': 'Carlos', 'tipo': 'COORDENADOR'},
}
env.globals.update(ctx_global)

conn2 = sqlite3.connect(':memory:')
conn2.row_factory = sqlite3.Row
conn2.executescript(SCHEMA_SQLITE)
carrega_inserts(conn2)


def q(sql):
    return [dict(r) for r in conn2.execute(sql).fetchall()]


grade_rows = q("""SELECT a.id_alocacao, p.numero AS periodo, d.codigo AS cod_disciplina,
 d.nome AS disciplina, u.nome AS professor, ds.abreviacao AS dia, h.slot,
 s.bloco || '-' || s.numero AS sala
 FROM alocacao a JOIN disciplina d ON d.id_disciplina=a.id_disciplina
 JOIN periodo p ON p.id_periodo=d.id_periodo
 JOIN professor pr ON pr.id_professor=a.id_professor
 JOIN usuario u ON u.id_usuario=pr.id_usuario
 JOIN horario h ON h.id_horario=a.id_horario
 JOIN dia_semana ds ON ds.id_dia=h.id_dia
 JOIN sala s ON s.id_sala=a.id_sala""")
dias = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
matriz = {d: {1: [], 2: []} for d in dias}
for l in grade_rows:
    matriz[l['dia']][l['slot']].append(l)

contextos = {
    'login.html': {},
    'usuarios.html': {'usuarios': q('SELECT * FROM usuario')},
    'habilitacoes.html': {
        'professores': q('SELECT pr.id_professor, u.nome FROM professor pr JOIN usuario u ON u.id_usuario=pr.id_usuario'),
        'disciplinas': q('SELECT d.id_disciplina, d.codigo, d.nome, p.numero AS periodo FROM disciplina d JOIN periodo p ON p.id_periodo=d.id_periodo'),
        'habilitacoes': q('SELECT u.nome AS professor, d.codigo, d.nome AS disciplina, pd.id_professor, pd.id_disciplina FROM professor_disciplina pd JOIN professor pr ON pr.id_professor=pd.id_professor JOIN usuario u ON u.id_usuario=pr.id_usuario JOIN disciplina d ON d.id_disciplina=pd.id_disciplina'),
    },
    'grade.html': {'matriz': matriz, 'dias': dias, 'total': len(grade_rows)},
    'relatorio.html': {'carga': [{'professor': 'Ana', 'titulacao': 'Doutora',
                                  'qtde_disciplinas': 3, 'carga_horaria_total': 220,
                                  'total_alunos': 8}]},
}
for tpl, ctx in contextos.items():
    html = env.get_template(tpl).render(**ctx)
    assert len(html) > 200, tpl
    print(f'OK {tpl} ({len(html)} bytes)')

print('\nTodos os testes offline passaram.')
