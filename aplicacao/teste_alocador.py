# -*- coding: utf-8 -*-
"""Teste do algoritmo de alocacao com os dados de carga (02_inserts.sql).
Valida todas as restricoes e imprime a grade resultante."""
from alocador import (gerar_grade, estatisticas, atribuir_professores,
                      construir_grafo)

PERIODO_DISC = {1: [1, 2, 3, 4], 2: [5, 6, 7, 8], 3: [9, 10, 11, 12],
                4: [13, 14, 15, 16], 5: [17, 18, 19, 20]}

NOMES = {1: 'ALG1', 2: 'LOG1', 3: 'MTD1', 4: 'IADS', 5: 'ALG2', 6: 'BD1',
         7: 'POO1', 8: 'ARC1', 9: 'BD2', 10: 'WEB1', 11: 'ENG1', 12: 'SO1',
         13: 'MOB1', 14: 'RED1', 15: 'GPR1', 16: 'SEG1', 17: 'IA1',
         18: 'NUV1', 19: 'TI1', 20: 'TOP1'}

PROFS = {1: 'Ana', 2: 'Bruno', 3: 'Camila', 4: 'Daniel', 5: 'Elaine',
         6: 'Fabio', 7: 'Gabriela', 8: 'Henrique'}

HORARIOS = {1: 'SEG 19:00', 2: 'SEG 20:55', 3: 'TER 19:00', 4: 'TER 20:55',
            5: 'QUA 19:00', 6: 'QUA 20:55', 7: 'QUI 19:00', 8: 'QUI 20:55',
            9: 'SEX 19:00', 10: 'SEX 20:55'}

disciplinas = [{'id': d, 'nome': NOMES[d], 'id_periodo': p}
               for p, ds in PERIODO_DISC.items() for d in ds]

# habilitacoes identicas ao script 02_inserts.sql
habilitacoes = {}
pares = [(1, 1), (1, 2), (1, 5), (2, 3), (2, 8), (2, 12), (3, 6), (3, 9),
         (3, 17), (4, 10), (4, 13), (4, 4), (5, 11), (5, 15), (5, 19),
         (6, 14), (6, 16), (6, 18), (7, 7), (7, 20), (7, 10), (8, 17),
         (8, 12), (8, 5), (8, 1)]
for prof, disc in pares:
    habilitacoes.setdefault(disc, []).append(prof)

SALAS = [1, 2, 3, 4, 5, 6]

# ------------------------- execucao -------------------------
alocacoes = gerar_grade(disciplinas, habilitacoes, SALAS)

# ------------------------- validacoes -------------------------
erros = []
periodo_de = {d['id']: d['id_periodo'] for d in disciplinas}
slot_ocup = {}
for a in alocacoes:
    # professor habilitado?
    if a['id_professor'] not in habilitacoes[a['id_disciplina']]:
        erros.append(f"Prof nao habilitado: {a}")
    slot_ocup.setdefault(a['id_horario'], []).append(a)

for slot, items in slot_ocup.items():
    profs = [a['id_professor'] for a in items]
    pers = [periodo_de[a['id_disciplina']] for a in items]
    salas = [a['id_sala'] for a in items]
    if len(profs) != len(set(profs)):
        erros.append(f'Slot {slot}: professor em duas disciplinas simultaneas')
    if len(pers) != len(set(pers)):
        erros.append(f'Slot {slot}: duas disciplinas do mesmo periodo')
    if len(salas) != len(set(salas)):
        erros.append(f'Slot {slot}: sala duplicada')

discs_alocadas = {a['id_disciplina'] for a in alocacoes}
if discs_alocadas != set(NOMES):
    erros.append('Nem todas as disciplinas foram alocadas')

print('=' * 70)
print('GRADE DE HORARIOS GERADA - 2026/1')
print('=' * 70)
for slot in sorted(slot_ocup):
    print(f'\n{HORARIOS[slot]} (horario {slot}):')
    for a in sorted(slot_ocup[slot], key=lambda x: periodo_de[x['id_disciplina']]):
        d = a['id_disciplina']
        print(f"  P{periodo_de[d]} | {NOMES[d]:5s} | Prof. {PROFS[a['id_professor']]:9s} | Sala {a['id_sala']}")

print('\n' + '=' * 70)
est = estatisticas(alocacoes)
print(f"Slots usados: {est['slots_usados']} de 10")
print(f"Paralelismo medio: {est['paralelismo_medio']} disciplinas por slot")
print(f"Disciplinas por slot: {est['disciplinas_por_slot']}")
print('\nVALIDACAO:', 'OK - nenhuma restricao violada' if not erros else erros)

# ------------------------- gera SQL -------------------------
print('\n--- INSERTs gerados (alocacao) ---')
linhas = []
for i, a in enumerate(alocacoes, 1):
    linhas.append(f" ({i},{a['id_disciplina']},{a['id_professor']},"
                  f"{a['id_horario']},{a['id_sala']},1)")
sql = ("SET IDENTITY_INSERT alocacao ON;\n"
       "INSERT INTO alocacao (id_alocacao, id_disciplina, id_professor, "
       "id_horario, id_sala, id_semestre) VALUES\n"
       + ',\n'.join(linhas) + ";\nSET IDENTITY_INSERT alocacao OFF;")
print(sql)

# matriculas: cada aluno matricula-se nas disciplinas do seu periodo atual
ALUNOS = {1: 1, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}  # id_aluno: periodo_atual
aloc_por_disc = {a['id_disciplina']: i for i, a in enumerate(alocacoes, 1)}
m_linhas = []
mid = 0
for aluno, per in ALUNOS.items():
    for d in PERIODO_DISC[per]:
        mid += 1
        m_linhas.append(f" ({mid},{aluno},{aloc_por_disc[d]},'2026-01-20','ATIVA')")
msql = ("SET IDENTITY_INSERT matricula ON;\n"
        "INSERT INTO matricula (id_matricula, id_aluno, id_alocacao, "
        "data_matricula, status) VALUES\n"
        + ',\n'.join(m_linhas) + ";\nSET IDENTITY_INSERT matricula OFF;")
print('\n--- INSERTs gerados (matricula) ---')
print(msql)
