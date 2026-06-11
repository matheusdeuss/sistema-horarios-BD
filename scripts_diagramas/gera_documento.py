# -*- coding: utf-8 -*-
"""Gera o documento final do trabalho (Trabalho_Final_BD.docx)."""
import os
import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(BASE, '..')
DOC_DIR = os.path.join(RAIZ, 'documentacao')
SQL_DIR = os.path.join(RAIZ, 'sql')
APP_DIR = os.path.join(RAIZ, 'aplicacao')

AZUL = RGBColor(0x1C, 0x3F, 0x94)

doc = Document()

# ---------- estilos ----------
normal = doc.styles['Normal']
normal.font.name = 'Calibri'
normal.font.size = Pt(11)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15

for nome, tam in [('Heading 1', 16), ('Heading 2', 13), ('Heading 3', 11.5)]:
    h = doc.styles[nome]
    h.font.name = 'Calibri'
    h.font.size = Pt(tam)
    h.font.bold = True
    h.font.color.rgb = AZUL

cod = doc.styles.add_style('Codigo', WD_STYLE_TYPE.PARAGRAPH)
cod.font.name = 'Consolas'
cod.font.size = Pt(8)
cod.paragraph_format.space_after = Pt(0)
cod.paragraph_format.line_spacing = 1.0
cod.paragraph_format.left_indent = Cm(0.4)

leg = doc.styles.add_style('Legenda', WD_STYLE_TYPE.PARAGRAPH)
leg.font.size = Pt(9)
leg.font.italic = True
leg.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER


def p(texto, estilo=None, negrito=False):
    par = doc.add_paragraph(style=estilo)
    run = par.add_run(texto)
    run.bold = negrito
    return par


def codigo(texto, max_linhas=None):
    linhas = texto.rstrip().splitlines()
    if max_linhas and len(linhas) > max_linhas:
        linhas = linhas[:max_linhas] + ['... (continua no arquivo do projeto)']
    for l in linhas:
        doc.add_paragraph(l if l.strip() else ' ', style='Codigo')
    doc.add_paragraph(style='Normal')


def arquivo(caminho):
    with open(caminho, encoding='utf-8') as f:
        return f.read()


def secao_sql(texto_sql):
    """Divide o arquivo de consultas em blocos (comentario, sql)."""
    blocos = []
    for b in re.split(r'/\*', texto_sql)[1:]:
        if '*/' not in b:
            continue
        comentario, resto = b.split('*/', 1)
        sql = resto.strip().rstrip(';')
        sql = sql.split('/*')[0].strip()
        blocos.append((comentario.strip(), sql))
    return blocos


# ============================ CAPA ============================
for _ in range(4):
    doc.add_paragraph()
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run('PONTIFÍCIA UNIVERSIDADE CATÓLICA DE MINAS GERAIS\n'
              'Instituto de Ciências Exatas e Informática (ICEI)\n'
              'Tecnologia em Análise e Desenvolvimento de Sistemas')
r.bold = True
r.font.size = Pt(13)
doc.add_paragraph()
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run('SISTEMA DE GESTÃO DE HORÁRIOS DE DISCIPLINAS')
r.bold = True
r.font.size = Pt(20)
r.font.color.rgb = AZUL
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
t.add_run('Trabalho Final (Interdisciplinar) — Banco de Dados — Semestre 1/2026').font.size = Pt(12)
for _ in range(6):
    doc.add_paragraph()
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
t.add_run('Integrantes do grupo:\n'
          '_______________________________________\n'
          '_______________________________________\n'
          '_______________________________________\n'
          '_______________________________________\n'
          '_______________________________________').font.size = Pt(12)
doc.add_paragraph()
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
t.add_run('Belo Horizonte — Junho de 2026').font.size = Pt(11)
doc.add_page_break()

# ============================ 1 INTRODUCAO ============================
doc.add_heading('1. Introdução', level=1)
p('A montagem do quadro de horários de um curso superior é um problema clássico de '
  'alocação de recursos com restrições (timetabling). No contexto do curso de Tecnologia em '
  'Análise e Desenvolvimento de Sistemas (ADS) da PUC Minas, o coordenador precisa, a cada '
  'semestre letivo, atribuir a cada disciplina um professor habilitado, um horário e uma '
  'sala, respeitando um conjunto de regras: disciplinas do mesmo período não podem ocorrer '
  'no mesmo horário (pois os alunos do período precisam cursá-las todas); um professor não '
  'pode ministrar duas aulas simultaneamente; cada disciplina é ministrada por exatamente '
  'um professor; e há apenas dois horários de aula por dia. Ao mesmo tempo, deseja-se '
  'maximizar o número de disciplinas oferecidas em paralelo, compactando a grade e '
  'aproveitando melhor os horários disponíveis.')
p('Este trabalho apresenta a especificação e a implementação de um Sistema de Gestão de '
  'Horários de Disciplinas que apoia esse processo. O sistema contempla o cadastro e a '
  'autenticação de usuários, o gerenciamento das habilitações de professores, a geração '
  'automática da grade de horários por meio de um algoritmo baseado em coloração de grafos '
  'e a consulta da grade resultante.')
doc.add_heading('1.1 Objetivos', level=2)
p('Objetivo geral: especificar e implementar um sistema de informação para a gestão de '
  'horários de disciplinas do curso de ADS, com banco de dados relacional projetado segundo '
  'as etapas de modelagem conceitual, lógica e física.')
p('Objetivos específicos: (i) elaborar o diagrama entidade-relacionamento e o diagrama de '
  'classes do sistema; (ii) mapear o modelo conceitual para o modelo relacional normalizado, '
  'com no mínimo 10 tabelas; (iii) implementar o modelo físico em SQL Server, com chaves '
  'primárias, estrangeiras, restrições e gatilhos; (iv) desenvolver as consultas SQL '
  'exigidas na especificação (junções, operações de conjuntos, agregações, operadores LIKE/'
  'BETWEEN/IN e visões); (v) projetar e implementar o algoritmo de alocação de horários; e '
  '(vi) desenvolver uma aplicação web conectada ao banco de dados com pelo menos três '
  'funcionalidades.')
doc.add_heading('1.2 Linhas gerais do desenvolvimento', level=2)
p('O desenvolvimento seguiu as etapas clássicas de projeto de banco de dados: levantamento '
  'de requisitos, modelagem conceitual (DER e diagrama de classes), mapeamento lógico '
  '(esquema relacional normalizado), implementação física (scripts DDL em T-SQL), '
  'desenvolvimento das consultas e, por fim, implementação da aplicação web em Python '
  '(Flask) conectada ao SQL Server via pyodbc. O problema de alocação foi modelado como um '
  'problema de coloração de grafos e resolvido com a heurística gulosa de Welsh-Powell.')

# ============================ 2 REQUISITOS ============================
doc.add_heading('2. Requisitos do sistema', level=1)
doc.add_heading('2.1 Requisitos funcionais', level=2)
rfs = [
    'RF01 — O sistema deve gerenciar o cadastro de usuários (coordenador, professores e alunos).',
    'RF02 — O sistema deve realizar a autenticação de usuários por login e senha.',
    'RF03 — O sistema deve manter o cadastro de cursos, períodos e disciplinas.',
    'RF04 — O sistema deve registrar as habilitações de cada professor (disciplinas que está apto a ministrar).',
    'RF05 — O sistema deve gerar automaticamente a grade de horários do semestre, alocando professor, horário e sala para cada disciplina, maximizando o número de disciplinas em paralelo.',
    'RF06 — O sistema deve impedir que disciplinas do mesmo período sejam alocadas no mesmo horário.',
    'RF07 — O sistema deve garantir que cada disciplina seja ministrada por exatamente um professor habilitado.',
    'RF08 — O sistema deve permitir a visualização da grade de horários e de relatórios de carga docente.',
    'RF09 — O sistema deve permitir a matrícula de alunos nas disciplinas alocadas.',
]
for rf in rfs:
    doc.add_paragraph(rf, style='List Bullet')
doc.add_heading('2.2 Requisitos não funcionais', level=2)
rnfs = [
    'RNF01 — O banco de dados deve ser implementado no SGBD Microsoft SQL Server.',
    'RNF02 — A aplicação deve ser web, desenvolvida em Python com o microframework Flask.',
    'RNF03 — As regras de validação devem ser implementadas no código da aplicação e também no SGBD, por meio de constraints e triggers.',
    'RNF04 — Não é exigida criptografia de senhas (conforme especificação do trabalho).',
    'RNF05 — A geração da grade deve responder em tempo adequado para o porte do problema (20 disciplinas, 10 horários).',
]
for rnf in rnfs:
    doc.add_paragraph(rnf, style='List Bullet')

# ============================ 3 MODELAGEM CONCEITUAL ============================
doc.add_heading('3. Modelagem conceitual', level=1)
p('O domínio foi modelado com 12 entidades principais. O núcleo do modelo é a entidade '
  'associativa ALOCACAO, que relaciona DISCIPLINA, PROFESSOR, HORARIO, SALA e '
  'SEMESTRE_LETIVO — ela representa uma "aula publicada" na grade. USUARIO generaliza os '
  'papéis do sistema, com PROFESSOR e ALUNO como especializações (relacionamentos 1:1). O '
  'relacionamento N:M "habilitado" entre PROFESSOR e DISCIPLINA registra quais disciplinas '
  'cada professor pode ministrar; já o professor que efetivamente ministra a disciplina no '
  'semestre é definido na ALOCACAO. Cada HORARIO pertence a um DIA_SEMANA e possui um slot '
  '(1 ou 2), refletindo a regra de dois horários de alocação por dia.')
doc.add_heading('3.1 Diagrama Entidade-Relacionamento (DER)', level=2)
doc.add_picture(os.path.join(DOC_DIR, 'DER.png'), width=Cm(16.5))
doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p('Figura 1 — Diagrama Entidade-Relacionamento do sistema.', estilo='Legenda')
doc.add_heading('3.2 Diagrama de Classes', level=2)
p('O diagrama de classes detalha atributos e métodos. Destaca-se a classe de serviço '
  'AlocadorHorarios, responsável pelo algoritmo de geração da grade (atribuição de '
  'professores, construção do grafo de conflitos e coloração).')
doc.add_picture(os.path.join(DOC_DIR, 'DiagramaClasses.png'), width=Cm(16.5))
doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p('Figura 2 — Diagrama de Classes do sistema.', estilo='Legenda')

# ============================ 4 MODELO LOGICO ============================
doc.add_heading('4. Mapeamento para o modelo lógico (relacional)', level=1)
p('O mapeamento do DER para o esquema relacional seguiu as regras clássicas: entidades '
  'viram relações; relacionamentos 1:N são mapeados com chave estrangeira no lado N; o '
  'relacionamento N:M "habilitado" vira a relação PROFESSOR_DISCIPLINA; as especializações '
  'PROFESSOR e ALUNO viram relações próprias com chave estrangeira única para USUARIO. O '
  'esquema resultante possui 13 tabelas e está na 3ª Forma Normal: todos os atributos são '
  'atômicos (1FN), não há dependências parciais de chaves compostas (2FN) e não há '
  'dependências transitivas — atributos descritivos como nome de professor ou de dia da '
  'semana residem apenas nas tabelas correspondentes (3FN).')
p('Convenção: chave primária sublinhada indicada como PK; chaves estrangeiras como FK.')
esquema = """usuario(id_usuario PK, nome, email UQ, login UQ, senha, tipo_usuario)
curso(id_curso PK, nome, sigla UQ, total_periodos)
periodo(id_periodo PK, id_curso FK->curso, numero)  UQ(id_curso, numero)
disciplina(id_disciplina PK, id_periodo FK->periodo, codigo UQ, nome, carga_horaria)
professor(id_professor PK, id_usuario FK->usuario UQ, matricula UQ, titulacao, data_admissao)
professor_disciplina(id_professor PK FK->professor, id_disciplina PK FK->disciplina)
semestre_letivo(id_semestre PK, ano, semestre, data_inicio, data_fim)  UQ(ano, semestre)
dia_semana(id_dia PK, nome UQ, abreviacao)
horario(id_horario PK, id_dia FK->dia_semana, slot, hora_inicio, hora_fim)  UQ(id_dia, slot)
sala(id_sala PK, numero, bloco, capacidade, tipo)  UQ(numero, bloco)
aluno(id_aluno PK, id_usuario FK->usuario UQ, id_curso FK->curso, matricula UQ, periodo_atual)
alocacao(id_alocacao PK, id_disciplina FK->disciplina, id_professor FK->professor,
         id_horario FK->horario, id_sala FK->sala, id_semestre FK->semestre_letivo,
         data_criacao)
         UQ(id_disciplina, id_semestre)        -- 1 professor por disciplina
         UQ(id_professor, id_horario, id_semestre)  -- professor sem choque de horario
         UQ(id_sala, id_horario, id_semestre)       -- sala sem choque de horario
matricula(id_matricula PK, id_aluno FK->aluno, id_alocacao FK->alocacao,
          data_matricula, status)  UQ(id_aluno, id_alocacao)"""
codigo(esquema)

# ============================ 5 MODELO FISICO ============================
doc.add_heading('5. Modelo físico — scripts DDL (SQL Server)', level=1)
p('O script completo encontra-se em sql/01_ddl.sql. Além das chaves primárias e '
  'estrangeiras, foram criadas restrições UNIQUE que materializam as regras de negócio na '
  'tabela alocacao e dois triggers: trg_valida_periodo_horario (impede disciplinas do mesmo '
  'período no mesmo horário — RF06) e trg_valida_habilitacao (garante que o professor '
  'alocado esteja habilitado para a disciplina — RF07). A seguir, o script DDL integral:')
codigo(arquivo(os.path.join(SQL_DIR, '01_ddl.sql')))
p('A carga de dados de teste (sql/02_inserts.sql) povoa o banco com 1 curso (ADS, 5 '
  'períodos), 20 disciplinas, 8 professores, 25 habilitações, 10 horários (5 dias × 2 '
  'slots), 6 salas, 15 usuários, 6 alunos, a grade gerada pelo algoritmo (20 alocações) e '
  '24 matrículas.')

# ============================ 6 ALGORITMO ============================
doc.add_heading('6. Solução do problema de alocação de horários', level=1)
doc.add_heading('6.1 Modelagem do problema', level=2)
p('O problema foi modelado como COLORAÇÃO DE GRAFO DE CONFLITOS. Cada disciplina é um '
  'vértice do grafo; existe uma aresta entre duas disciplinas quando elas não podem ocupar '
  'o mesmo horário, o que ocorre em duas situações: (a) pertencem ao mesmo período do curso '
  '(os alunos precisam assistir a ambas), ou (b) serão ministradas pelo mesmo professor '
  '(ele não pode estar em duas salas ao mesmo tempo). Cada cor corresponde a um dos 10 '
  'horários disponíveis (5 dias × 2 horários por dia). Uma coloração válida em que vértices '
  'adjacentes recebem cores distintas é exatamente uma grade sem conflitos; minimizar o '
  'número de cores utilizadas equivale a maximizar o número médio de disciplinas em '
  'paralelo, que é o objetivo do trabalho.')
p('Antes da coloração, é resolvido um subproblema: atribuir exatamente um professor a cada '
  'disciplina, escolhido entre os habilitados. A estratégia adotada processa primeiro as '
  'disciplinas mais restritas (com menos professores habilitados) e atribui sempre o '
  'professor habilitado com menor carga acumulada. Isso equilibra a carga docente e reduz o '
  'número de arestas do grafo, favorecendo o paralelismo.')
doc.add_heading('6.2 Pseudocódigo', level=2)
pseudocodigo = """ALGORITMO GerarGrade(disciplinas, habilitacoes, salas)
  // Fase 1 - atribuicao de professores (guloso por restritividade)
  ordenar disciplinas por |habilitacoes(d)| crescente
  para cada disciplina d:
      prof(d) <- professor habilitado em d com menor carga atual
      carga(prof(d)) <- carga(prof(d)) + 1

  // Fase 2 - grafo de conflitos
  para cada par (d1, d2) de disciplinas:
      se periodo(d1) = periodo(d2) OU prof(d1) = prof(d2):
          adicionar aresta {d1, d2}

  // Fase 3 - coloracao gulosa (Welsh-Powell)
  ordenar vertices por grau decrescente
  para cada vertice v:
      slot(v) <- menor cor em {1..10} nao usada pelos vizinhos de v
      se nao existe cor disponivel: FALHA (mais de 10 conflitos mutuos)

  // Fase 4 - atribuicao de salas
  para cada slot s, em ordem:
      atribuir a cada disciplina do slot uma sala distinta ainda livre em s

  retornar { (d, prof(d), slot(d), sala(d)) para cada disciplina d }
FIM"""
codigo(pseudocodigo)
doc.add_heading('6.3 Análise', level=2)
p('A coloração mínima de grafos é um problema NP-difícil; a heurística de Welsh-Powell não '
  'garante o ótimo, mas produz soluções de boa qualidade em tempo O(V² + V·C), adequado ao '
  'porte do problema. No estudo de caso, o limite inferior teórico é de 5 cores (o grafo '
  'contém cliques de tamanho 5, pois há períodos com 4 disciplinas cujos professores também '
  'lecionam em outros períodos) e o algoritmo alcançou exatamente 5 horários, com '
  'paralelismo médio de 4,0 disciplinas por horário.')
doc.add_heading('6.4 Código-fonte do algoritmo (alocador.py)', level=2)
codigo(arquivo(os.path.join(APP_DIR, 'alocador.py')))

# ============================ 7 CONSULTAS ============================
doc.add_heading('7. Consultas em SQL', level=1)
p('Todas as consultas envolvem no mínimo três tabelas, conforme exigido. Cada consulta é '
  'apresentada com a explicação do que faz (extraída do arquivo sql/03_consultas.sql).')

titulos_blocos = {
    'J': '7.1 Consultas de junção',
    'C': '7.2 Consultas de operações de conjuntos',
    'A': '7.3 Consultas de agregação',
    'L': '7.4 Consultas com LIKE, BETWEEN e IN',
}
ultimo_bloco = ''
texto_consultas = arquivo(os.path.join(SQL_DIR, '03_consultas.sql'))
for comentario, sql in secao_sql(texto_consultas):
    primeira = comentario.splitlines()[0].strip()
    m = re.match(r'([JCAL])\d\)', primeira)
    if not m:
        continue
    if m.group(1) != ultimo_bloco:
        ultimo_bloco = m.group(1)
        doc.add_heading(titulos_blocos[ultimo_bloco], level=2)
    doc.add_heading(primeira, level=3)
    explic = ' '.join(l.strip() for l in comentario.splitlines()[1:] if l.strip())
    p(explic)
    codigo(sql)

doc.add_heading('7.5 Visões', level=2)
texto_views = arquivo(os.path.join(SQL_DIR, '04_views.sql'))
for comentario, sql in secao_sql(texto_views):
    primeira = comentario.splitlines()[0].strip()
    if not re.match(r'V\d\)', primeira):
        continue
    doc.add_heading(primeira, level=3)
    explic = ' '.join(l.strip() for l in comentario.splitlines()[1:] if l.strip())
    p(explic)
    codigo(sql + ';')

# ============================ 8 APLICACAO ============================
doc.add_heading('8. Implementação da aplicação web', level=1)
p('A aplicação foi desenvolvida em Python 3 com o microframework Flask e conecta-se ao SQL '
  'Server por meio da biblioteca pyodbc (módulo db.py). A interface utiliza templates '
  'Jinja2. Foram implementadas quatro funcionalidades:')
funcs = [
    'F1 — Cadastro de usuários: formulário com validação no código da aplicação (nome, formato de e-mail, tamanho de login e senha, unicidade de login/e-mail) antes do INSERT.',
    'F2 — Autenticação de usuários: login e senha verificados no banco; sessão Flask controla o acesso — todas as demais páginas exigem usuário autenticado.',
    'F3 — Gestão de habilitações professor × disciplina: inclusão e remoção de registros na tabela professor_disciplina, com verificação de duplicidade.',
    'F4 — Geração e visualização da grade: o coordenador aciona o algoritmo de alocação; as alocações são gravadas na tabela alocacao dentro de uma transação e a grade é exibida em uma matriz dia × horário alimentada pela visão vw_grade_horarios.',
]
for f in funcs:
    doc.add_paragraph(f, style='List Bullet')
p('Além da validação na aplicação, as regras críticas são garantidas no SGBD: restrições '
  'UNIQUE da tabela alocacao e os triggers trg_valida_periodo_horario e '
  'trg_valida_habilitacao rejeitam qualquer inserção que viole as regras, mesmo que feita '
  'fora da aplicação. O código-fonte completo está na pasta aplicacao/ do projeto '
  '(app.py, db.py, alocador.py e templates).')
doc.add_heading('8.1 Trecho principal — geração da grade (app.py)', level=2)
trecho_app = """@app.route('/grade/gerar', methods=['POST'])
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
    for par in pares:
        habilitacoes_.setdefault(par['id_disciplina'], []).append(par['id_professor'])

    try:
        alocacoes = gerar_grade(disciplinas, habilitacoes_, salas)
    except ValueError as e:
        flash(f'Falha na geracao da grade: {e}', 'erro')
        return redirect(url_for('grade'))

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
        conn.commit()"""
codigo(trecho_app)

# ============================ 9 TESTES ============================
doc.add_heading('9. Testes e resultados', level=1)
doc.add_heading('9.1 Teste do algoritmo de alocação', level=2)
p('O algoritmo foi executado com os dados de teste (20 disciplinas em 5 períodos, 8 '
  'professores, 25 habilitações, 10 horários e 6 salas — script teste_alocador.py). '
  'Resultado: as 20 disciplinas foram alocadas em apenas 5 dos 10 horários disponíveis, com '
  'paralelismo médio de 4,0 disciplinas por horário e nenhuma restrição violada (verificação '
  'automática de choques de período, de professor e de sala). Grade gerada:')
grade_txt = """SEG 19:00 -> P1 IADS (Daniel)    P2 BD1 (Camila)   P3 ENG1 (Elaine)   P5 NUV1 (Fabio)
SEG 20:55 -> P1 ALG1 (Henrique)  P2 ALG2 (Ana)     P3 BD2 (Camila)    P4 MOB1 (Daniel)  P5 TI1 (Elaine)
TER 19:00 -> P1 LOG1 (Ana)       P2 POO1 (Gabriela) P3 WEB1 (Daniel)  P4 GPR1 (Elaine)  P5 IA1 (Camila)
TER 20:55 -> P1 MTD1 (Bruno)     P3 SO1 (Henrique) P4 RED1 (Fabio)    P5 TOP1 (Gabriela)
QUA 19:00 -> P2 ARC1 (Bruno)     P4 SEG1 (Fabio)

Slots usados: 5 de 10 | Paralelismo medio: 4.0 | Validacao: OK"""
codigo(grade_txt)
p('Vale notar que o resultado atinge o ótimo teórico para esta instância: como cada um dos '
  '5 períodos possui 4 disciplinas e há professores compartilhados entre períodos, são '
  'necessários pelo menos 5 horários; o algoritmo utilizou exatamente 5.')
doc.add_heading('9.2 Teste das consultas SQL', level=2)
p('As 12 consultas e as 2 visões foram executadas sobre a carga de dados de teste '
  '(script teste_consultas.py) e todas retornaram resultados corretos e não vazios. '
  'Resumo dos resultados:')
resultados = [
    ('J1 — Grade completa de horários', '20 linhas (uma por alocação)'),
    ('J2 — Disciplinas matriculadas por aluno', '24 linhas (4 disciplinas × 6 alunos)'),
    ('C1 — UNION: pessoas com vínculo no semestre', '14 linhas (8 professores + 6 alunos)'),
    ('C2 — INTERSECT: habilitados em P1/P2 e alocados', '6 professores'),
    ('C3 — EXCEPT: habilitações não utilizadas', '5 pares professor × disciplina'),
    ('A1 — COUNT/GROUP BY/HAVING: professores com 2+ disciplinas', '8 linhas (todos ministram 2 ou 3)'),
    ('A2 — AVG/MIN/MAX/HAVING: carga horária por período', '4 períodos com média >= 60 h'),
    ('A3 — COUNT/GROUP BY: paralelismo por horário', '5 horários (4, 5, 5, 4 e 2 disciplinas)'),
    ('A4 — SUM/GROUP BY: carga horária por professor', '8 linhas (máx. 220 h, mín. 120 h)'),
    ('L1 — LIKE \'%Dados%\'', '4 disciplinas (ALG1, ALG2, BD1, BD2)'),
    ('L2 — BETWEEN 2012 e 2018 (admissão)', '11 linhas'),
    ('L3 — IN (\'SEG\',\'SEX\')', '9 alocações de segunda (nenhuma na sexta)'),
    ('V1 — vw_grade_horarios', '20 linhas'),
    ('V2 — vw_carga_professores', '8 linhas'),
]
tab = doc.add_table(rows=1, cols=2)
tab.style = 'Light Grid Accent 1'
hdr = tab.rows[0].cells
hdr[0].text = 'Consulta'
hdr[1].text = 'Resultado obtido'
for nome, res in resultados:
    cels = tab.add_row().cells
    cels[0].text = nome
    cels[1].text = res
doc.add_paragraph()
doc.add_heading('9.3 Teste das regras de validação', level=2)
p('Os triggers foram exercitados com inserções inválidas: a tentativa de alocar uma segunda '
  'disciplina do 1º período no mesmo horário foi rejeitada com a mensagem "Conflito: já '
  'existe disciplina do mesmo período alocada neste horário"; a tentativa de alocar um '
  'professor sem habilitação foi rejeitada por trg_valida_habilitacao. As restrições UNIQUE '
  'da tabela alocacao bloquearam choques de professor e de sala no mesmo horário. Na '
  'aplicação, o cadastro de usuários rejeitou e-mails malformados, logins duplicados e '
  'senhas com menos de 6 caracteres.')

# ============================ 10 CONCLUSAO ============================
doc.add_heading('10. Conclusão', level=1)
p('O trabalho cobriu o ciclo completo de projeto de um sistema de banco de dados: da '
  'modelagem conceitual à aplicação final. A observação mais importante é o valor de '
  'modelar formalmente o problema de negócio: ao enxergar a montagem da grade como '
  'coloração de grafos, uma exigência aparentemente complexa ("maximizar disciplinas em '
  'paralelo respeitando conflitos") tornou-se um algoritmo simples, eficiente e verificável, '
  'que atingiu o ótimo teórico na instância de teste (20 disciplinas em 5 horários, '
  'paralelismo médio 4,0).')
p('Também ficou evidente a importância de implementar regras de negócio em camadas '
  'redundantes: as validações da aplicação oferecem boas mensagens ao usuário, enquanto '
  'constraints e triggers no SGBD garantem a integridade mesmo diante de acessos diretos ao '
  'banco. Por fim, o uso de visões simplificou a aplicação, encapsulando junções de até 9 '
  'tabelas em consultas de uma linha. Como trabalhos futuros, sugerem-se: suporte a múltiplos '
  'cursos e turnos, preferências de horário por professor e métodos exatos (programação '
  'inteira) para comparação com a heurística.')

# ============================ 11 REFERENCIAS ============================
doc.add_heading('11. Referências', level=1)
refs = [
    'ELMASRI, R.; NAVATHE, S. B. Sistemas de Banco de Dados. 7. ed. São Paulo: Pearson, 2018.',
    'SILBERSCHATZ, A.; KORTH, H. F.; SUDARSHAN, S. Sistemas de Banco de Dados. 7. ed. Rio de Janeiro: LTC, 2020.',
    'WELSH, D. J. A.; POWELL, M. B. An upper bound for the chromatic number of a graph and its application to timetabling problems. The Computer Journal, v. 10, n. 1, p. 85-86, 1967.',
    'MICROSOFT. Documentação do SQL Server. Disponível em: https://learn.microsoft.com/sql. Acesso em: jun. 2026.',
    'PALLETS PROJECTS. Flask Documentation. Disponível em: https://flask.palletsprojects.com. Acesso em: jun. 2026.',
]
for r_ in refs:
    doc.add_paragraph(r_, style='List Bullet')

saida = os.path.join(DOC_DIR, 'Trabalho_Final_BD.docx')
doc.save(saida)
print('Documento gerado:', saida)
