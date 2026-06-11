# -*- coding: utf-8 -*-
"""Gera o Diagrama Entidade-Relacionamento (notacao de Chen simplificada)."""
import graphviz

g = graphviz.Graph('DER', format='png', engine='dot')
g.attr(rankdir='LR', splines='polyline', nodesep='0.45', ranksep='0.9',
       fontname='Helvetica', dpi='150', bgcolor='white',
       label='Diagrama Entidade-Relacionamento - Sistema de Gestão de Horários (ADS/PUC Minas)',
       labelloc='t', fontsize='20')

ENT = dict(shape='record', style='filled', fillcolor='#DDEBF7',
           color='#2E75B6', fontname='Helvetica', fontsize='11')
REL = dict(shape='diamond', style='filled', fillcolor='#FFF2CC',
           color='#BF9000', fontname='Helvetica', fontsize='10',
           height='0.7', width='1.4')

def ent(name, attrs):
    attrs = [a.replace('<u>', '').replace('</u>', '') for a in attrs]
    label = '{' + name + '|' + '\\l'.join(attrs) + '\\l}'
    g.node(name, label=label, **ENT)

ent('USUARIO', ['<u>id_usuario</u> (PK)', 'nome', 'email', 'login', 'senha', 'tipo_usuario'])
ent('PROFESSOR', ['<u>id_professor</u> (PK)', 'matricula', 'titulacao', 'data_admissao'])
ent('ALUNO', ['<u>id_aluno</u> (PK)', 'matricula', 'periodo_atual'])
ent('CURSO', ['<u>id_curso</u> (PK)', 'nome', 'sigla', 'total_periodos'])
ent('PERIODO', ['<u>id_periodo</u> (PK)', 'numero'])
ent('DISCIPLINA', ['<u>id_disciplina</u> (PK)', 'codigo', 'nome', 'carga_horaria'])
ent('SEMESTRE_LETIVO', ['<u>id_semestre</u> (PK)', 'ano', 'semestre', 'data_inicio', 'data_fim'])
ent('DIA_SEMANA', ['<u>id_dia</u> (PK)', 'nome', 'abreviacao'])
ent('HORARIO', ['<u>id_horario</u> (PK)', 'slot', 'hora_inicio', 'hora_fim'])
ent('SALA', ['<u>id_sala</u> (PK)', 'numero', 'bloco', 'capacidade', 'tipo'])
ent('ALOCACAO', ['<u>id_alocacao</u> (PK)', 'data_criacao'])
ent('MATRICULA', ['<u>id_matricula</u> (PK)', 'data_matricula', 'status'])

rels = [
    ('USUARIO', 'eh_prof', 'PROFESSOR', '1', '1'),
    ('USUARIO', 'eh_aluno', 'ALUNO', '1', '1'),
    ('CURSO', 'possui', 'PERIODO', '1', 'N'),
    ('PERIODO', 'contem', 'DISCIPLINA', '1', 'N'),
    ('CURSO', 'oferece', 'ALUNO', '1', 'N'),
    ('PROFESSOR', 'habilitado', 'DISCIPLINA', 'N', 'M'),
    ('DISCIPLINA', 'alocada_em', 'ALOCACAO', '1', 'N'),
    ('PROFESSOR', 'ministra', 'ALOCACAO', '1', 'N'),
    ('HORARIO', 'ocorre_em', 'ALOCACAO', '1', 'N'),
    ('SALA', 'utiliza', 'ALOCACAO', '1', 'N'),
    ('SEMESTRE_LETIVO', 'vigente_em', 'ALOCACAO', '1', 'N'),
    ('DIA_SEMANA', 'define', 'HORARIO', '1', 'N'),
    ('ALUNO', 'matriculado', 'MATRICULA', '1', 'N'),
    ('ALOCACAO', 'gera', 'MATRICULA', '1', 'N'),
]
for a, r, b, ca, cb in rels:
    rid = f'rel_{r}'
    g.node(rid, label=r, **REL)
    g.edge(a, rid, label=ca, fontname='Helvetica', fontsize='10')
    g.edge(rid, b, label=cb, fontname='Helvetica', fontsize='10')

g.render('/tmp/DER', cleanup=True)
print('DER gerado')
