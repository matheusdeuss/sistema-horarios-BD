# -*- coding: utf-8 -*-
"""Gera o Diagrama de Classes (UML) do sistema."""
import graphviz

g = graphviz.Digraph('Classes', format='png', engine='dot')
g.attr(rankdir='TB', splines='ortho', nodesep='0.5', ranksep='0.8',
       fontname='Helvetica', dpi='150', bgcolor='white',
       label='Diagrama de Classes - Sistema de Gestão de Horários (ADS/PUC Minas)',
       labelloc='t', fontsize='20')

NODE = dict(shape='record', style='filled', fillcolor='#E2EFDA',
            color='#548235', fontname='Helvetica', fontsize='11')

def cls(name, attrs, methods):
    label = '{' + name + '|' + '\\l'.join(attrs) + '\\l|' + '\\l'.join(methods) + '\\l}'
    g.node(name, label=label, **NODE)

cls('Usuario',
    ['- idUsuario: int', '- nome: String', '- email: String', '- login: String',
     '- senha: String', '- tipoUsuario: String'],
    ['+ autenticar(login, senha): bool', '+ cadastrar(): void', '+ atualizarDados(): void'])

cls('Professor',
    ['- idProfessor: int', '- matricula: String', '- titulacao: String', '- dataAdmissao: Date'],
    ['+ adicionarHabilitacao(d: Disciplina): void', '+ listarDisciplinasHabilitadas(): List',
     '+ consultarGrade(s: SemestreLetivo): List'])

cls('Aluno',
    ['- idAluno: int', '- matricula: String', '- periodoAtual: int'],
    ['+ matricular(a: Alocacao): Matricula', '+ consultarHorario(): List'])

cls('Curso',
    ['- idCurso: int', '- nome: String', '- sigla: String', '- totalPeriodos: int'],
    ['+ listarPeriodos(): List', '+ listarDisciplinas(): List'])

cls('Periodo',
    ['- idPeriodo: int', '- numero: int'],
    ['+ listarDisciplinas(): List'])

cls('Disciplina',
    ['- idDisciplina: int', '- codigo: String', '- nome: String', '- cargaHoraria: int'],
    ['+ listarProfessoresHabilitados(): List', '+ estaAlocada(s: SemestreLetivo): bool'])

cls('SemestreLetivo',
    ['- idSemestre: int', '- ano: int', '- semestre: int',
     '- dataInicio: Date', '- dataFim: Date'],
    ['+ obterGradeCompleta(): List'])

cls('DiaSemana',
    ['- idDia: int', '- nome: String', '- abreviacao: String'],
    [' '])

cls('Horario',
    ['- idHorario: int', '- slot: int', '- horaInicio: Time', '- horaFim: Time'],
    ['+ descricao(): String'])

cls('Sala',
    ['- idSala: int', '- numero: String', '- bloco: String',
     '- capacidade: int', '- tipo: String'],
    ['+ estaDisponivel(h: Horario, s: SemestreLetivo): bool'])

cls('Alocacao',
    ['- idAlocacao: int', '- dataCriacao: DateTime'],
    ['+ validarConflitos(): bool', '+ confirmar(): void', '+ cancelar(): void'])

cls('Matricula',
    ['- idMatricula: int', '- dataMatricula: Date', '- status: String'],
    ['+ cancelar(): void'])

cls('AlocadorHorarios',
    ['- alocacoes: List<Alocacao>', '- slotsDisponiveis: int'],
    ['+ atribuirProfessores(): Map', '+ construirGrafoConflitos(): Graph',
     '+ colorirGrafo(): Map', '+ gerarGrade(s: SemestreLetivo): List<Alocacao>'])

# Heranca (generalizacao)
g.edge('Professor', 'Usuario', arrowhead='onormal', arrowsize='1.4')
g.edge('Aluno', 'Usuario', arrowhead='onormal', arrowsize='1.4')

def assoc(a, b, la='', lb='', label=''):
    g.edge(a, b, dir='none', taillabel=la, headlabel=lb, label=label,
           fontname='Helvetica', fontsize='10', labeldistance='1.8')

assoc('Curso', 'Periodo', '1', '1..*', 'possui')
assoc('Periodo', 'Disciplina', '1', '1..*', 'contém')
assoc('Curso', 'Aluno', '1', '0..*', 'oferece')
assoc('Professor', 'Disciplina', '1..*', '1..*', 'habilitado')
assoc('Disciplina', 'Alocacao', '1', '0..*')
assoc('Professor', 'Alocacao', '1', '0..*')
assoc('Horario', 'Alocacao', '1', '0..*')
assoc('Sala', 'Alocacao', '1', '0..*')
assoc('SemestreLetivo', 'Alocacao', '1', '0..*')
assoc('DiaSemana', 'Horario', '1', '2')
assoc('Aluno', 'Matricula', '1', '0..*')
assoc('Alocacao', 'Matricula', '1', '0..*')
g.edge('AlocadorHorarios', 'Alocacao', style='dashed', arrowhead='vee', label='cria',
       fontname='Helvetica', fontsize='10')

g.render('/tmp/DiagramaClasses', cleanup=True)
print('Diagrama de classes gerado')
