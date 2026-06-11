# -*- coding: utf-8 -*-
"""
Sistema de Gestao de Horarios - ADS/PUC Minas
Aplicacao web (Flask + SQL Server)

Funcionalidades implementadas:
  F1 - Cadastro de usuarios (com validacao no codigo da aplicacao)
  F2 - Autenticacao de usuarios (login/logout, controle de sessao)
  F3 - Gestao de habilitacoes professor x disciplina
  F4 - Geracao automatica da grade de horarios (algoritmo de coloracao
       de grafos) e visualizacao da grade

As regras de negocio criticas tambem sao garantidas no SGBD por
constraints UNIQUE e pelos triggers trg_valida_periodo_horario e
trg_valida_habilitacao (ver 01_ddl.sql).
"""
import re
from functools import wraps
from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash)
import db
from alocador import gerar_grade, estatisticas

app = Flask(__name__)
app.secret_key = 'trabalho-bd-2026'

SEMESTRE_ATUAL = 1  # id_semestre de 2026/1


# ----------------------------------------------------------------------
# Autenticacao (F2)
# ----------------------------------------------------------------------
def login_obrigatorio(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'id_usuario' not in session:
            flash('Faca login para acessar o sistema.', 'erro')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('grade') if 'id_usuario' in session else url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_ = request.form.get('login', '').strip()
        senha = request.form.get('senha', '')
        usuarios = db.consultar(
            'SELECT id_usuario, nome, tipo_usuario FROM usuario '
            'WHERE login = ? AND senha = ?', (login_, senha))
        if usuarios:
            u = usuarios[0]
            session['id_usuario'] = u['id_usuario']
            session['nome'] = u['nome']
            session['tipo'] = u['tipo_usuario']
            flash(f"Bem-vindo(a), {u['nome']}!", 'ok')
            return redirect(url_for('grade'))
        flash('Login ou senha invalidos.', 'erro')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Sessao encerrada.', 'ok')
    return redirect(url_for('login'))


# ----------------------------------------------------------------------
# Cadastro de usuarios (F1) - validacao no codigo da aplicacao
# ----------------------------------------------------------------------
def validar_usuario(form):
    erros = []
    if len(form.get('nome', '').strip()) < 3:
        erros.append('Nome deve ter pelo menos 3 caracteres.')
    if not re.match(r'^[\w.+-]+@[\w-]+\.[\w.-]+$', form.get('email', '')):
        erros.append('E-mail invalido.')
    if not re.match(r'^[a-zA-Z0-9_.]{3,30}$', form.get('login', '')):
        erros.append('Login deve ter 3 a 30 caracteres alfanumericos.')
    if len(form.get('senha', '')) < 6:
        erros.append('Senha deve ter pelo menos 6 caracteres.')
    if form.get('tipo_usuario') not in ('COORDENADOR', 'PROFESSOR', 'ALUNO'):
        erros.append('Tipo de usuario invalido.')
    return erros


@app.route('/usuarios', methods=['GET', 'POST'])
@login_obrigatorio
def usuarios():
    if request.method == 'POST':
        erros = validar_usuario(request.form)
        ja_existe = db.consultar(
            'SELECT 1 AS x FROM usuario WHERE login = ? OR email = ?',
            (request.form['login'], request.form['email']))
        if ja_existe:
            erros.append('Login ou e-mail ja cadastrado.')
        if erros:
            for e in erros:
                flash(e, 'erro')
        else:
            db.executar(
                'INSERT INTO usuario (nome, email, login, senha, tipo_usuario) '
                'VALUES (?,?,?,?,?)',
                (request.form['nome'].strip(), request.form['email'].strip(),
                 request.form['login'].strip(), request.form['senha'],
                 request.form['tipo_usuario']))
            flash('Usuario cadastrado com sucesso.', 'ok')
            return redirect(url_for('usuarios'))
    lista = db.consultar(
        'SELECT id_usuario, nome, email, login, tipo_usuario FROM usuario '
        'ORDER BY nome')
    return render_template('usuarios.html', usuarios=lista)


# ----------------------------------------------------------------------
# Habilitacoes professor x disciplina (F3)
# ----------------------------------------------------------------------
@app.route('/habilitacoes', methods=['GET', 'POST'])
@login_obrigatorio
def habilitacoes():
    if request.method == 'POST':
        id_prof = request.form.get('id_professor')
        id_disc = request.form.get('id_disciplina')
        if not id_prof or not id_disc:
            flash('Selecione professor e disciplina.', 'erro')
        else:
            existe = db.consultar(
                'SELECT 1 AS x FROM professor_disciplina '
                'WHERE id_professor = ? AND id_disciplina = ?', (id_prof, id_disc))
            if existe:
                flash('Habilitacao ja cadastrada.', 'erro')
            else:
                db.executar(
                    'INSERT INTO professor_disciplina (id_professor, id_disciplina) '
                    'VALUES (?,?)', (id_prof, id_disc))
                flash('Habilitacao cadastrada.', 'ok')
        return redirect(url_for('habilitacoes'))

    professores = db.consultar(
        'SELECT pr.id_professor, u.nome FROM professor pr '
        'JOIN usuario u ON u.id_usuario = pr.id_usuario ORDER BY u.nome')
    disciplinas = db.consultar(
        'SELECT d.id_disciplina, d.codigo, d.nome, p.numero AS periodo '
        'FROM disciplina d JOIN periodo p ON p.id_periodo = d.id_periodo '
        'ORDER BY p.numero, d.codigo')
    lista = db.consultar(
        'SELECT u.nome AS professor, d.codigo, d.nome AS disciplina, '
        '       pd.id_professor, pd.id_disciplina '
        'FROM professor_disciplina pd '
        'JOIN professor pr ON pr.id_professor = pd.id_professor '
        'JOIN usuario u    ON u.id_usuario    = pr.id_usuario '
        'JOIN disciplina d ON d.id_disciplina = pd.id_disciplina '
        'ORDER BY u.nome, d.codigo')
    return render_template('habilitacoes.html', professores=professores,
                           disciplinas=disciplinas, habilitacoes=lista)


@app.route('/habilitacoes/remover', methods=['POST'])
@login_obrigatorio
def remover_habilitacao():
    db.executar(
        'DELETE FROM professor_disciplina WHERE id_professor = ? AND id_disciplina = ?',
        (request.form['id_professor'], request.form['id_disciplina']))
    flash('Habilitacao removida.', 'ok')
    return redirect(url_for('habilitacoes'))


# ----------------------------------------------------------------------
# Geracao e visualizacao da grade (F4)
# ----------------------------------------------------------------------
@app.route('/grade')
@login_obrigatorio
def grade():
    linhas = db.consultar(
        'SELECT * FROM vw_grade_horarios ORDER BY dia, slot, periodo')
    # organiza em matriz dia x slot para exibicao
    dias = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
    matriz = {d: {1: [], 2: []} for d in dias}
    for l in linhas:
        matriz[l['dia']][l['slot']].append(l)
    return render_template('grade.html', matriz=matriz, dias=dias,
                           total=len(linhas))


@app.route('/grade/gerar', methods=['POST'])
@login_obrigatorio
def gerar():
    if session.get('tipo') != 'COORDENADOR':
        flash('Apenas o coordenador pode gerar a grade.', 'erro')
        return redirect(url_for('grade'))

    disciplinas = db.consultar(
        'SELECT id_disciplina AS id, nome, id_periodo FROM disciplina')
    pares = db.consultar(
        'SELECT id_professor, id_disciplina FROM professor_disciplina')
    salas = [s['id_sala'] for s in db.consultar('SELECT id_sala FROM sala')]

    habilitacoes_ = {}
    for p in pares:
        habilitacoes_.setdefault(p['id_disciplina'], []).append(p['id_professor'])

    try:
        alocacoes = gerar_grade(disciplinas, habilitacoes_, salas)
    except ValueError as e:
        flash(f'Falha na geracao da grade: {e}', 'erro')
        return redirect(url_for('grade'))

    # regenera a grade do semestre dentro de uma transacao
    with db.conectar() as conn:
        cur = conn.cursor()
        cur.execute('DELETE FROM matricula WHERE id_alocacao IN '
                    '(SELECT id_alocacao FROM alocacao WHERE id_semestre = ?)',
                    (SEMESTRE_ATUAL,))
        cur.execute('DELETE FROM alocacao WHERE id_semestre = ?', (SEMESTRE_ATUAL,))
        for a in alocacoes:
            cur.execute(
                'INSERT INTO alocacao (id_disciplina, id_professor, id_horario, '
                'id_sala, id_semestre) VALUES (?,?,?,?,?)',
                (a['id_disciplina'], a['id_professor'], a['id_horario'],
                 a['id_sala'], SEMESTRE_ATUAL))
        conn.commit()

    est = estatisticas(alocacoes)
    flash(f"Grade gerada: {len(alocacoes)} disciplinas em "
          f"{est['slots_usados']} horarios (paralelismo medio "
          f"{est['paralelismo_medio']}).", 'ok')
    return redirect(url_for('grade'))


@app.route('/relatorio')
@login_obrigatorio
def relatorio():
    carga = db.consultar(
        'SELECT * FROM vw_carga_professores ORDER BY carga_horaria_total DESC')
    return render_template('relatorio.html', carga=carga)


if __name__ == '__main__':
    app.run(debug=True)
