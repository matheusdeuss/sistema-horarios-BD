# Preparação para a apresentação (11/06/2026)

Critérios de avaliação: qualidade da documentação (modelagem) + qualidade da implementação, com **nota individual** — todos do grupo devem saber explicar qualquer parte.

---

## 1. Perguntas prováveis sobre MODELAGEM

**P: Por que o esquema tem 13 tabelas? Como vocês chegaram nelas?**
R: Partimos das entidades do domínio (usuário, curso, período, disciplina, professor, aluno, sala, horário, semestre), aplicamos as regras de mapeamento: o relacionamento N:M "professor habilitado a disciplina" virou a tabela `professor_disciplina`; o relacionamento múltiplo disciplina–professor–horário–sala–semestre virou a entidade associativa `alocacao`; e `matricula` liga aluno à turma alocada. `dia_semana` é tabela de domínio (lookup) para evitar repetição de texto.

**P: Qual a diferença entre `professor_disciplina` e `alocacao`? Não é redundante?**
R: Não. `professor_disciplina` registra **capacidade** (quais disciplinas o professor PODE ministrar — vale para qualquer semestre). `alocacao` registra a **decisão** (quem efetivamente ministra a disciplina, em qual horário e sala, num semestre específico). São fatos diferentes, com tempos de vida diferentes.

**P: Como vocês mapearam a generalização Usuário → Professor/Aluno?**
R: Estratégia "uma tabela por especialização": `professor` e `aluno` têm chave própria e FK **com restrição UNIQUE** para `usuario`, garantindo o 1:1. Dados comuns (nome, login, senha) ficam só em `usuario` — sem redundância.

**P: O esquema está em qual forma normal? Justifique.**
R: 3FN. 1FN: todos os atributos são atômicos. 2FN: a única chave composta é a de `professor_disciplina`, que não tem atributos além da chave — sem dependência parcial. 3FN: não há dependências transitivas — ex.: o nome do professor não está em `alocacao`, está só em `usuario`; o período da disciplina está só em `disciplina`.

**P: Para que servem as 3 restrições UNIQUE da tabela `alocacao`?**
R: Cada uma materializa uma regra do enunciado:
- `UQ(id_disciplina, id_semestre)` → uma disciplina tem **um único professor** (uma única alocação por semestre);
- `UQ(id_professor, id_horario, id_semestre)` → professor não pode estar em dois lugares no mesmo horário;
- `UQ(id_sala, id_horario, id_semestre)` → sala não recebe duas turmas simultâneas.

**P: Por que a regra "disciplinas do mesmo período não podem estar no mesmo horário" foi feita com TRIGGER e não com constraint?**
R: Porque ela depende de informação de **outra tabela** (o período está em `disciplina`, não em `alocacao`). Constraints UNIQUE/CHECK só enxergam a própria linha/tabela; a verificação exige junção, então usamos o trigger `trg_valida_periodo_horario`, que rejeita o INSERT/UPDATE com ROLLBACK.

**P: Qual a diferença entre o DER e o diagrama de classes?**
R: O DER modela os **dados persistentes** e seus relacionamentos (visão de banco). O diagrama de classes é a visão de **software**: inclui métodos e a classe de serviço `AlocadorHorarios`, que não vira tabela — é lógica de negócio, não dado.

---

## 2. Perguntas prováveis sobre SQL

**P: Diferença entre UNION e UNION ALL?**
R: UNION elimina duplicatas (faz ordenação/hash interno); UNION ALL apenas concatena. Usamos UNION em C1 porque a mesma pessoa não deve aparecer duas vezes.

**P: O que INTERSECT e EXCEPT fazem? Dava para escrever sem eles?**
R: INTERSECT retorna linhas presentes nos dois resultados; EXCEPT, as do primeiro que não estão no segundo. Sim: INTERSECT ≈ IN/EXISTS, EXCEPT ≈ NOT IN/NOT EXISTS — mas os operadores de conjunto deixam a intenção explícita e comparam a tupla inteira.

**P: Diferença entre WHERE e HAVING?**
R: WHERE filtra **linhas antes** do agrupamento; HAVING filtra **grupos depois** do GROUP BY, podendo usar funções de agregação (ex.: `HAVING AVG(carga_horaria) >= 60` em A2).

**P: Por que criar visões?**
R: Encapsulam junções complexas (a `vw_grade_horarios` junta 9 tabelas), simplificam a aplicação (o app faz `SELECT * FROM vw_grade_horarios`), e permitem controle de acesso — pode-se dar permissão na view sem expor as tabelas base.

**P: Por que LEFT JOIN com `matricula` na `vw_carga_professores`?**
R: Para que professores com turmas ainda **sem alunos matriculados** apareçam no relatório (com total_alunos = 0). Com INNER JOIN eles sumiriam.

**P: Como a aplicação evita SQL Injection?**
R: Todas as consultas usam **parâmetros** (`?` do pyodbc) — o valor nunca é concatenado na string SQL.

---

## 3. Perguntas prováveis sobre o ALGORITMO

**P: Como vocês modelaram o problema de alocação?**
R: Como **coloração de grafo de conflitos**. Cada disciplina é um vértice; há aresta quando duas disciplinas não podem dividir horário (mesmo período OU mesmo professor); cada cor é um dos 10 horários (5 dias × 2). Uma coloração válida = grade sem conflitos. Minimizar cores = maximizar disciplinas em paralelo (objetivo do enunciado).

**P: Por que um algoritmo guloso e não busca exaustiva?**
R: Coloração mínima de grafos é **NP-difícil** — força bruta seria 10^20 combinações para 20 disciplinas. A heurística de Welsh-Powell (ordenar vértices por grau decrescente e dar a cada um a menor cor livre) roda em O(V²) e dá soluções muito boas na prática.

**P: O algoritmo garante a solução ótima?**
R: Não garante em geral. Mas na nossa instância **atingiu o ótimo provável**: o grafo contém cliques de tamanho 5 (limite inferior de 5 cores) e o algoritmo usou exatamente 5 horários, com paralelismo médio 4,0.

**P: Por que atribuir professores ANTES de colorir o grafo?**
R: Porque as arestas de conflito docente dependem de quem ministra o quê. Atribuímos primeiro as disciplinas mais restritas (menos habilitados) ao professor habilitado com menor carga — isso equilibra a carga e **reduz arestas**, facilitando a coloração.

**P: E se não houver horário disponível (mais de 10 conflitos mútuos)?**
R: O algoritmo lança erro tratado; a aplicação mostra a mensagem ao usuário sem alterar o banco. Aconteceria, por ex., se um período tivesse 11 disciplinas.

---

## 4. Perguntas prováveis sobre a APLICAÇÃO

**P: Como a aplicação conecta ao banco?**
R: Python + Flask; módulo `db.py` usa **pyodbc** com connection string para o SQL Server (driver ODBC). As consultas retornam dicionários consumidos pelos templates Jinja2.

**P: Onde estão as validações?**
R: Em duas camadas (defesa em profundidade): no **código da aplicação** (formato de e-mail, tamanho de senha, duplicidade de login — com mensagens amigáveis) e no **SGBD** (constraints UNIQUE/CHECK + 2 triggers), que protegem mesmo se alguém inserir dados direto pelo SSMS.

**P: Por que a senha está sem criptografia?**
R: A especificação do trabalho dispensou explicitamente. Em produção usaríamos hash com salt (bcrypt/argon2) — nunca senha em texto puro.

**P: Por que a geração da grade usa transação?**
R: Ela apaga a grade anterior e insere a nova (DELETE + 20 INSERTs). A transação garante **atomicidade**: ou tudo, ou nada — sem risco de grade pela metade se algo falhar.

---

## 5. Roteiro sugerido de apresentação (~10 min)

1. **Problema e requisitos** (1 min) — alocação de horários do ADS; regras: 2 horários/dia, sem choque de período, 1 professor por disciplina, maximizar paralelismo.
2. **Modelagem** (2 min) — mostrar DER; destacar `alocacao` como núcleo, habilitação vs alocação, herança de usuário.
3. **Modelo físico** (1,5 min) — abrir `01_ddl.sql` no SSMS; mostrar os 3 UNIQUEs de `alocacao` e um trigger.
4. **Algoritmo** (2 min) — explicar coloração de grafos com o pseudocódigo; mostrar resultado: 20 disciplinas em 5 horários, ótimo.
5. **Demo ao vivo** (2,5 min) — login → cadastrar um usuário (mostrar validação falhando de propósito: e-mail inválido) → gerar grade → mostrar a grade na tela → relatório de carga docente.
6. **Consultas** (1 min) — rodar no SSMS 1 junção (J1), 1 de conjunto (C3) e 1 agregação (A1), lendo a explicação de cada uma.
7. **Conclusão** (30 s) — modelar o problema formalmente simplificou a solução; regras em camadas redundantes garantem integridade.

### Demonstração "à prova de pergunta"
Tenha pronto no SSMS um INSERT **inválido** para mostrar o trigger funcionando:
```sql
-- tenta alocar 2a disciplina do periodo 1 no horario 1 (ja tem IADS)
INSERT INTO alocacao (id_disciplina, id_professor, id_horario, id_sala, id_semestre)
VALUES (1, 8, 1, 6, 1);
-- Erro esperado: "Conflito: ja existe disciplina do mesmo periodo alocada neste horario."
```

### Checklist antes da aula
- [ ] Scripts rodados no SQL Server da máquina da apresentação (01 → 02 → 04)
- [ ] `db.py` ajustado e conexão testada
- [ ] App abrindo em http://localhost:5000 (login carlos/123456)
- [ ] Nomes do grupo preenchidos na capa do documento
- [ ] Cada integrante sabe responder pelo menos as seções 1 e 3 deste guia
