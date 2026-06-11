# -*- coding: utf-8 -*-
"""Valida as consultas SQL (03_consultas.sql e 04_views.sql) executando-as
em um banco SQLite com o mesmo esquema e os mesmos dados do SQL Server.
Unica adaptacao de dialeto: concatenacao ('+' -> '||').
Gera o arquivo resultados_consultas.txt com a saida de cada consulta."""
import re
import sqlite3
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SQL_DIR = os.path.join(BASE, '..', 'sql')

SCHEMA_SQLITE = """
CREATE TABLE usuario (id_usuario INTEGER PRIMARY KEY, nome TEXT, email TEXT UNIQUE,
  login TEXT UNIQUE, senha TEXT, tipo_usuario TEXT);
CREATE TABLE curso (id_curso INTEGER PRIMARY KEY, nome TEXT, sigla TEXT UNIQUE, total_periodos INT);
CREATE TABLE periodo (id_periodo INTEGER PRIMARY KEY, id_curso INT REFERENCES curso, numero INT,
  UNIQUE (id_curso, numero));
CREATE TABLE disciplina (id_disciplina INTEGER PRIMARY KEY, id_periodo INT REFERENCES periodo,
  codigo TEXT UNIQUE, nome TEXT, carga_horaria INT);
CREATE TABLE professor (id_professor INTEGER PRIMARY KEY, id_usuario INT UNIQUE REFERENCES usuario,
  matricula TEXT UNIQUE, titulacao TEXT, data_admissao TEXT);
CREATE TABLE professor_disciplina (id_professor INT REFERENCES professor,
  id_disciplina INT REFERENCES disciplina, PRIMARY KEY (id_professor, id_disciplina));
CREATE TABLE semestre_letivo (id_semestre INTEGER PRIMARY KEY, ano INT, semestre INT,
  data_inicio TEXT, data_fim TEXT, UNIQUE (ano, semestre));
CREATE TABLE dia_semana (id_dia INTEGER PRIMARY KEY, nome TEXT UNIQUE, abreviacao TEXT);
CREATE TABLE horario (id_horario INTEGER PRIMARY KEY, id_dia INT REFERENCES dia_semana,
  slot INT, hora_inicio TEXT, hora_fim TEXT, UNIQUE (id_dia, slot));
CREATE TABLE sala (id_sala INTEGER PRIMARY KEY, numero TEXT, bloco TEXT, capacidade INT,
  tipo TEXT, UNIQUE (numero, bloco));
CREATE TABLE aluno (id_aluno INTEGER PRIMARY KEY, id_usuario INT UNIQUE REFERENCES usuario,
  id_curso INT REFERENCES curso, matricula TEXT UNIQUE, periodo_atual INT);
CREATE TABLE alocacao (id_alocacao INTEGER PRIMARY KEY, id_disciplina INT REFERENCES disciplina,
  id_professor INT REFERENCES professor, id_horario INT REFERENCES horario,
  id_sala INT REFERENCES sala, id_semestre INT REFERENCES semestre_letivo,
  data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (id_disciplina, id_semestre),
  UNIQUE (id_professor, id_horario, id_semestre),
  UNIQUE (id_sala, id_horario, id_semestre));
CREATE TABLE matricula (id_matricula INTEGER PRIMARY KEY, id_aluno INT REFERENCES aluno,
  id_alocacao INT REFERENCES alocacao, data_matricula TEXT, status TEXT DEFAULT 'ATIVA',
  UNIQUE (id_aluno, id_alocacao));
"""


def adapta(sql):
    """Adapta T-SQL -> SQLite (apenas concatenacao de strings)."""
    return sql.replace("s.bloco + '-' + s.numero", "s.bloco || '-' || s.numero")


def carrega_inserts(conn):
    with open(os.path.join(SQL_DIR, '02_inserts.sql'), encoding='utf-8') as f:
        texto = f.read()
    texto = re.sub(r'/\*.*?\*/', '', texto, flags=re.S)
    stmts = re.findall(r'INSERT INTO .*?;', texto, flags=re.S)
    for s in stmts:
        conn.execute(s)
    conn.commit()
    print(f'{len(stmts)} blocos de INSERT executados')


def extrai_consultas(arquivo):
    """Extrai pares (titulo, sql) do arquivo de consultas."""
    with open(os.path.join(SQL_DIR, arquivo), encoding='utf-8') as f:
        texto = f.read()
    texto = texto.replace('USE GestaoHorarios;', '').replace('\nGO\n', '\n')
    blocos = re.split(r'/\*', texto)
    consultas = []
    for b in blocos:
        if '*/' not in b:
            continue
        comentario, resto = b.split('*/', 1)
        m = re.match(r'\s*([A-Z]\d\)|V\d\))', comentario)
        titulo = comentario.strip().splitlines()[0].strip()
        sql = resto.strip().rstrip(';').strip()
        if m and sql and (sql.upper().startswith('SELECT') or sql.upper().startswith('CREATE VIEW')):
            consultas.append((titulo, sql))
    return consultas


def main():
    conn = sqlite3.connect(':memory:')
    conn.executescript(SCHEMA_SQLITE)
    carrega_inserts(conn)

    saida = []
    todas = [('03_consultas.sql', q) for q in extrai_consultas('03_consultas.sql')]
    todas += [('04_views.sql', q) for q in extrai_consultas('04_views.sql')]

    ok = 0
    for arq, (titulo, sql) in todas:
        sql_exec = adapta(sql)
        try:
            if sql_exec.upper().startswith('CREATE VIEW'):
                conn.executescript(sql_exec)
                nome_view = sql_exec.split()[2]
                cur = conn.execute(f'SELECT * FROM {nome_view}')
            else:
                cur = conn.execute(sql_exec)
            cols = [c[0] for c in cur.description]
            rows = cur.fetchall()
            ok += 1
            saida.append(f"\n{'=' * 78}\n{titulo}\n{'-' * 78}")
            saida.append(' | '.join(cols))
            for r in rows:
                saida.append(' | '.join(str(x) for x in r))
            saida.append(f'({len(rows)} linha(s))')
            print(f'OK   {titulo}  -> {len(rows)} linha(s)')
        except Exception as e:
            print(f'ERRO {titulo}: {e}')
            saida.append(f'\nERRO em {titulo}: {e}')

    with open(os.path.join(BASE, 'resultados_consultas.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(saida))
    print(f'\n{ok}/{len(todas)} consultas executadas com sucesso.')
    print('Resultados salvos em resultados_consultas.txt')


if __name__ == '__main__':
    main()
