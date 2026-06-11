# -*- coding: utf-8 -*-
"""Camada de acesso a dados - conexao com SQL Server via pyodbc."""
import pyodbc

# Ajuste os parametros conforme o seu ambiente
SERVER = r'DESKTOP-IDL4V8G\MSSQLSERVERR' # r'localhost\SQLEXPRESS' ou apenas 'localhost'
DATABASE = 'GestaoHorarios'
DRIVER = 'SQL Server'  # 'ODBC Driver 17 for SQL Server' ou 'SQL Server'

CONN_STR = (
    f'DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};'
    'UID=sa;PWD=matheus050724;' #'Trusted_Connection=yes;' # autenticacao Windows; para SQL auth use UID=...;PWD=...
)


def conectar():
    return pyodbc.connect(CONN_STR)


def consultar(sql, params=()):
    """Executa SELECT e retorna lista de dicts."""
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def executar(sql, params=()):
    """Executa INSERT/UPDATE/DELETE com commit."""
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.rowcount
