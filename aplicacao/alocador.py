# -*- coding: utf-8 -*-
"""
Algoritmo de alocacao de horarios - Sistema de Gestao de Horarios (ADS/PUC Minas)

O problema e modelado como COLORACAO DE GRAFO DE CONFLITOS:
  * Cada disciplina e um vertice.
  * Existe aresta entre duas disciplinas quando elas NAO podem ocupar o
    mesmo horario: (a) pertencem ao mesmo periodo, ou (b) serao
    ministradas pelo mesmo professor.
  * Cada cor corresponde a um horario (slot). Ha 10 slots disponiveis
    (5 dias x 2 horarios por dia).

Minimizar o numero de cores usadas equivale a MAXIMIZAR o numero medio de
disciplinas ministradas em paralelo. Usa-se a heuristica gulosa de
Welsh-Powell (vertices em ordem decrescente de grau).

Antes da coloracao, cada disciplina recebe exatamente UM professor entre
os habilitados, escolhido de forma a equilibrar a carga (professor
habilitado com menos disciplinas atribuidas), o que reduz o numero de
arestas do grafo e favorece o paralelismo.
"""


def atribuir_professores(disciplinas, habilitacoes):
    """Atribui um unico professor a cada disciplina.

    disciplinas  : lista de dicts {id, nome, id_periodo}
    habilitacoes : dict {id_disciplina: [id_professor, ...]}
    Retorna dict {id_disciplina: id_professor}.
    Estrategia gulosa: processa primeiro as disciplinas com MENOS
    professores habilitados (mais restritas) e escolhe o professor
    habilitado com MENOR carga atual.
    """
    carga = {}
    atribuicao = {}
    ordem = sorted(disciplinas, key=lambda d: len(habilitacoes.get(d['id'], [])))
    for d in ordem:
        candidatos = habilitacoes.get(d['id'], [])
        if not candidatos:
            raise ValueError(
                f"Disciplina {d['nome']} (id={d['id']}) nao possui professor habilitado.")
        professor = min(candidatos, key=lambda p: carga.get(p, 0))
        atribuicao[d['id']] = professor
        carga[professor] = carga.get(professor, 0) + 1
    return atribuicao


def construir_grafo(disciplinas, atribuicao):
    """Monta o grafo de conflitos (lista de adjacencia).

    Ha conflito (aresta) entre d1 e d2 se:
      * mesmo periodo  -> alunos nao podem assistir as duas ao mesmo tempo;
      * mesmo professor -> ele nao pode estar em duas salas ao mesmo tempo.
    """
    grafo = {d['id']: set() for d in disciplinas}
    for i, d1 in enumerate(disciplinas):
        for d2 in disciplinas[i + 1:]:
            mesmo_periodo = d1['id_periodo'] == d2['id_periodo']
            mesmo_professor = atribuicao[d1['id']] == atribuicao[d2['id']]
            if mesmo_periodo or mesmo_professor:
                grafo[d1['id']].add(d2['id'])
                grafo[d2['id']].add(d1['id'])
    return grafo


def colorir_grafo(grafo, num_slots=10):
    """Coloracao gulosa de Welsh-Powell.

    Ordena os vertices por grau decrescente e atribui a cada um a menor
    cor (slot) que nao conflite com seus vizinhos ja coloridos.
    Retorna dict {id_disciplina: slot} com slot em 1..num_slots.
    """
    cores = {}
    ordem = sorted(grafo, key=lambda v: len(grafo[v]), reverse=True)
    for v in ordem:
        usadas = {cores[u] for u in grafo[v] if u in cores}
        slot = next((c for c in range(1, num_slots + 1) if c not in usadas), None)
        if slot is None:
            raise ValueError(
                f'Nao ha slot disponivel para a disciplina id={v} '
                f'(limite de {num_slots} horarios excedido).')
        cores[v] = slot
    return cores


def atribuir_salas(cores, salas):
    """Distribui as salas: em cada slot, cada disciplina recebe uma sala
    distinta (ordem deterministica por id da disciplina)."""
    resultado = {}
    por_slot = {}
    for disc, slot in sorted(cores.items()):
        usadas = por_slot.setdefault(slot, set())
        sala = next((s for s in salas if s not in usadas), None)
        if sala is None:
            raise ValueError(f'Sem sala disponivel no slot {slot}.')
        usadas.add(sala)
        resultado[disc] = sala
    return resultado


def gerar_grade(disciplinas, habilitacoes, salas, num_slots=10):
    """Pipeline completo. Retorna lista de alocacoes:
    [{'id_disciplina', 'id_professor', 'id_horario', 'id_sala'}, ...]
    O id_horario corresponde diretamente ao slot (1..10), conforme a
    tabela horario carregada (5 dias x 2 slots).
    """
    atribuicao = atribuir_professores(disciplinas, habilitacoes)
    grafo = construir_grafo(disciplinas, atribuicao)
    cores = colorir_grafo(grafo, num_slots)
    salas_disc = atribuir_salas(cores, salas)
    return [
        {
            'id_disciplina': d['id'],
            'id_professor': atribuicao[d['id']],
            'id_horario': cores[d['id']],
            'id_sala': salas_disc[d['id']],
        }
        for d in sorted(disciplinas, key=lambda x: x['id'])
    ]


def estatisticas(alocacoes):
    """Resumo: ocupacao por slot (paralelismo)."""
    por_slot = {}
    for a in alocacoes:
        por_slot.setdefault(a['id_horario'], []).append(a['id_disciplina'])
    usados = len(por_slot)
    paralelismo_medio = len(alocacoes) / usados if usados else 0
    return {
        'slots_usados': usados,
        'paralelismo_medio': round(paralelismo_medio, 2),
        'disciplinas_por_slot': {s: len(ds) for s, ds in sorted(por_slot.items())},
    }
