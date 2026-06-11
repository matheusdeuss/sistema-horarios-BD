# Roteiro de apresentação + Revisão teórica

> Como usar: leia o roteiro em voz alta 2 ou 3 vezes hoje. Não decore palavra por palavra —
> decore a **sequência de ideias** de cada slide (estão em negrito). A revisão teórica da
> Parte 2 é o seu "porquê" de cada frase do roteiro: se entender ela, nenhuma pergunta te derruba.

---

# PARTE 1 — ROTEIRO (fala sugerida, slide a slide)

## Slide 1 — Capa (~20s)
> "Bom dia/Boa tarde. Nosso trabalho é um Sistema de Gestão de Horários de Disciplinas
> para o curso de ADS. O foco da apresentação vai ser em duas coisas: a qualidade da
> modelagem do banco de dados e a implementação — o DDL, as consultas e o algoritmo
> que monta a grade automaticamente."

**Ideia-chave: apresentar o tema e anunciar o foco (modelagem + implementação).**

## Slide 2 — O problema (~1min)
> "O problema que recebemos é o seguinte: montar o horário do curso de ADS. Parece
> simples, mas tem quatro restrições que se cruzam. Primeira: cada disciplina é
> ministrada por exatamente um professor, e ele precisa estar habilitado nela.
> Segunda: disciplinas do mesmo período não podem cair no mesmo horário — porque o
> aluno do 1º período, por exemplo, precisa cursar as quatro disciplinas do 1º período,
> então elas não podem se sobrepor. Terceira: um professor não pode estar em duas salas
> ao mesmo tempo. E quarta: só existem dois horários por dia, então a semana inteira
> tem só 10 horários.
>
> E além de respeitar tudo isso, o objetivo é maximizar o número de disciplinas em
> paralelo — ou seja, compactar a grade, aproveitar cada horário ao máximo."

**Ideia-chave: 4 restrições + objetivo de maximizar paralelismo.**

## Slide 3 — Visão geral (~40s)
> "Nossa solução seguiu o ciclo completo de projeto de banco de dados que vimos na
> disciplina: começamos pela modelagem conceitual — DER e diagrama de classes —,
> mapeamos para o modelo lógico relacional, que ficou com 13 tabelas normalizadas,
> implementamos o modelo físico em SQL Server com o script DDL, desenvolvemos as
> consultas SQL exigidas, e por fim o algoritmo de alocação e a aplicação web em
> Python que conecta tudo."

**Ideia-chave: conceitual → lógico → físico → consultas → aplicação.**

## Slide 4 — DER (~1min)
> "Esse é o nosso DER. Eu quero chamar atenção para o centro do diagrama: a entidade
> ALOCACAO. Ela é uma entidade associativa que liga cinco coisas: a disciplina, o
> professor, o horário, a sala e o semestre letivo. Cada linha de ALOCACAO é
> literalmente uma 'aula publicada' na grade: a disciplina X, com o professor Y, no
> horário Z, na sala W, no semestre 2026/1.
>
> Outros dois pontos: USUARIO é uma generalização — professor e aluno são
> especializações dele, num relacionamento um-para-um. E o HORARIO pertence a um
> DIA_SEMANA e tem um campo slot que só aceita 1 ou 2 — é assim que a regra dos
> 'dois horários por dia' entra no modelo."

**Ideia-chave: ALOCACAO é o coração; herança de USUARIO; slot 1/2 modela a regra do dia.**

## Slide 5 — Decisões de modelagem (~1min30)
> "Aqui estão as três decisões de modelagem que a gente considera mais importantes.
>
> A primeira: separar habilitação de alocação. A tabela PROFESSOR_DISCIPLINA diz quem
> PODE ministrar cada disciplina — é uma capacidade, vale para qualquer semestre. Já a
> ALOCACAO diz quem efetivamente MINISTRA, onde e quando, num semestre específico.
> São fatos diferentes, com tempos de vida diferentes, então viraram tabelas diferentes.
>
> A segunda: a herança. Professor e aluno compartilham nome, e-mail, login e senha —
> isso fica só na tabela USUARIO. As tabelas PROFESSOR e ALUNO têm uma chave
> estrangeira com restrição UNIQUE apontando para USUARIO, o que garante o
> um-para-um. Resultado: zero redundância.
>
> A terceira: transformar regra de negócio em estrutura. Por exemplo, 'dois horários
> por dia' não é um comentário no código — é uma constraint UNIQUE(dia, slot) com um
> CHECK que só aceita slot 1 ou 2. A regra mora no esquema."

**Ideia-chave: habilitação ≠ alocação; herança 1:1 sem redundância; regra vira constraint.**

## Slide 6 — Normalização (~1min)
> "Sobre normalização: o esquema está na Terceira Forma Normal, e dá pra justificar
> rapidamente. Primeira Forma: todos os atributos são atômicos — dias e horários são
> linhas de tabelas próprias, não tem lista nem texto composto. Segunda Forma: a única
> chave composta do esquema é a de PROFESSOR_DISCIPLINA, e ela não tem nenhum
> atributo fora da chave, então não existe dependência parcial. E Terceira Forma: não
> há dependência transitiva — o nome do professor está só em USUARIO, o período da
> disciplina está só em DISCIPLINA. A tabela ALOCACAO guarda só chaves estrangeiras,
> nenhum dado descritivo repetido."

**Ideia-chave: 1FN atômico, 2FN sem dependência parcial, 3FN sem transitiva — com os exemplos.**

## Slide 7 — DDL / ALOCACAO (~1min30) — *slide mais importante*
> "Agora o modelo físico. Essa é a tabela ALOCACAO no DDL, e eu quero mostrar como
> cada restrição do enunciado virou uma constraint que o próprio SGBD fiscaliza.
>
> O primeiro UNIQUE, de disciplina e semestre, garante que uma disciplina só tem uma
> alocação por semestre — ou seja, um único professor, exatamente como o enunciado pede.
>
> O segundo, de professor, horário e semestre, impede o professor de estar em dois
> lugares ao mesmo tempo: se o algoritmo ou qualquer pessoa tentar inserir duas
> alocações do mesmo professor no mesmo horário, o banco rejeita.
>
> E o terceiro faz o mesmo para a sala.
>
> O ponto central é: essas regras não dependem do programador lembrar de validar.
> Quem bloqueia o conflito é o SQL Server."

**Ideia-chave: cada UNIQUE = uma regra do enunciado; o banco se defende sozinho.**

## Slide 8 — Trigger (~1min30) — *2º slide mais importante*
> "Mas tem uma regra que constraint nenhuma consegue garantir: 'disciplinas do mesmo
> período não podem ficar no mesmo horário'. Por quê? Porque o período não está na
> tabela ALOCACAO — está na tabela DISCIPLINA. Constraints UNIQUE e CHECK só
> enxergam a própria linha, não fazem junção com outra tabela.
>
> A solução foi um trigger. O trg_valida_periodo_horario dispara depois de cada
> INSERT ou UPDATE em alocação, faz a junção com DISCIPLINA, e verifica: já existe
> outra alocação nesse mesmo horário e semestre cuja disciplina seja do mesmo período?
> Se existir, ele lança um erro e dá ROLLBACK — a transação inteira é desfeita.
>
> Com isso a gente tem validação em duas camadas: a aplicação valida e dá mensagem
> amigável pro usuário, e o SGBD garante a integridade mesmo se alguém inserir dados
> direto pelo Management Studio."

**Ideia-chave: constraint não cruza tabelas → trigger com junção + ROLLBACK; defesa em camadas.**

## Slide 9 — Panorama das consultas (~45s)
> "Sobre as consultas exigidas: fizemos as 12 consultas e as 2 visões, todas com no
> mínimo três tabelas. Duas de junção — a maior junta 8 tabelas pra montar a grade
> legível. Três de conjuntos, usando UNION, INTERSECT e EXCEPT. Quatro de agregação,
> cobrindo SUM, COUNT, MAX, MIN e AVG, duas delas com GROUP BY e HAVING. Três com
> LIKE, BETWEEN e IN. E duas visões, uma delas juntando 9 tabelas. Todas foram
> executadas com a carga de teste e todas retornaram resultados corretos."

**Ideia-chave: checklist completo da especificação, tudo testado.**

## Slide 10 — Consulta EXCEPT (~1min)
> "Escolhi essa pra detalhar porque ela mostra o valor dos operadores de conjunto.
> O primeiro SELECT lista todas as habilitações: todos os pares professor-disciplina
> em que o professor PODE ministrar. O segundo SELECT lista o que efetivamente está
> na grade. O EXCEPT devolve a diferença: as habilitações que NÃO estão sendo usadas
> neste semestre.
>
> Na prática isso é a 'capacidade ociosa' do quadro docente — se um professor ficar
> doente, essa consulta diz na hora quem pode substituí-lo. No nosso teste, retornou
> 5 pares."

**Ideia-chave: 1º bloco PODE, 2º bloco FAZ, EXCEPT = diferença = capacidade ociosa.**

## Slide 11 — Algoritmo (~1min30)
> "Pro problema da alocação em si, a gente modelou como coloração de grafos. Funciona
> assim: cada disciplina é um vértice. Eu ligo duas disciplinas com uma aresta quando
> elas NÃO podem ficar no mesmo horário — ou porque são do mesmo período, ou porque
> têm o mesmo professor. E cada cor é um dos 10 horários da semana.
>
> Colorir o grafo sem que vizinhos tenham a mesma cor é exatamente montar uma grade
> sem conflito. E usar menos cores significa mais disciplinas em paralelo — que é o
> objetivo do trabalho.
>
> Encontrar a coloração mínima é um problema NP-difícil, então usamos a heurística
> gulosa de Welsh-Powell: ordena os vértices do mais conflituoso pro menos, e dá a
> cada um a menor cor que não conflite com os vizinhos. Roda em tempo quadrático.
>
> Um detalhe importante: antes de colorir, a gente atribui os professores — começando
> pelas disciplinas com menos habilitados e sempre escolhendo o professor com menor
> carga. Isso equilibra a carga docente e reduz as arestas do grafo."

**Ideia-chave: disciplina=vértice, conflito=aresta, horário=cor; Welsh-Powell; professor antes.**

## Slide 12 — Resultados (~45s)
> "E o resultado: as 20 disciplinas foram alocadas usando só 5 dos 10 horários, com
> paralelismo médio de 4 disciplinas por horário e zero restrições violadas — a gente
> verifica isso automaticamente no teste.
>
> E tem um detalhe legal: 5 horários é o ótimo teórico dessa instância. O grafo contém
> grupos de 5 disciplinas todas em conflito entre si, então seriam necessários pelo
> menos 5 horários de qualquer jeito. A heurística chegou exatamente nesse limite."

**Ideia-chave: 20 disciplinas, 5/10 horários, paralelismo 4,0, ótimo teórico.**

## Slide 13 — Aplicação (~45s)
> "A aplicação web foi feita em Python com Flask, conectando no SQL Server via pyodbc.
> São quatro funcionalidades: cadastro de usuários com validação no código;
> autenticação com controle de sessão; gestão das habilitações; e a geração da grade,
> onde o coordenador clica um botão, o algoritmo roda e as alocações são gravadas no
> banco dentro de uma transação — ou grava tudo, ou nada.
>
> E um cuidado de implementação: todas as consultas usam parâmetros, nunca concatenação
> de string, então a aplicação está protegida contra SQL Injection."
>
> *(se houver demo: "Vou mostrar rapidamente funcionando...")*

**Ideia-chave: 4 funcionalidades; transação atômica; consultas parametrizadas.**

## Slide 14 — Conclusão (~40s)
> "Pra fechar, três aprendizados. Primeiro: modelar formalmente simplifica — quando a
> gente enxergou a grade como um grafo, um problema que parecia complicado virou um
> algoritmo de 100 linhas. Segundo: regra de negócio boa mora no esquema — com as
> constraints e os triggers, o banco se defende sozinho, não depende da aplicação.
> E terceiro: visões encapsulam complexidade — uma junção de 9 tabelas virou um
> SELECT de uma linha na aplicação.
>
> Era isso. Obrigado! Ficamos à disposição para perguntas."

**Ideia-chave: 3 lições; agradecer; abrir para perguntas.**

⏱️ **Tempo total: ~13 minutos.** Se precisar encurtar, corte os slides 3 e 10 (cai para ~11).

---

# PARTE 2 — REVISÃO TEÓRICA (entenda o porquê de cada coisa)

## 2.1 As três camadas de modelagem

| Camada | O que é | No nosso projeto |
|---|---|---|
| **Conceitual** | Descreve O QUE existe no domínio, sem pensar em SGBD. Entidades, atributos, relacionamentos, cardinalidades. | DER com 12 entidades |
| **Lógico** | Traduz para o modelo relacional: tabelas, colunas, chaves. Independente de fabricante. | 13 relações em 3FN |
| **Físico** | O DDL concreto de um SGBD específico: tipos de dados, constraints, índices, triggers. | Script T-SQL no SQL Server |

Por que separar? Porque decisões de negócio (conceitual) não devem se misturar com
decisões técnicas (físico). O DER conversa com o cliente; o DDL conversa com o servidor.

## 2.2 Conceitos do DER que usamos

- **Entidade**: coisa do domínio com existência própria (DISCIPLINA, SALA).
- **Entidade associativa**: relacionamento que virou entidade porque tem atributos e
  relacionamentos próprios. ALOCACAO liga 5 entidades e tem data_criacao.
- **Cardinalidade**: 1:1 (usuário–professor), 1:N (período–disciplina), N:M
  (professor–disciplina via habilitação).
- **Generalização/especialização**: USUARIO é o geral; PROFESSOR e ALUNO são casos
  específicos que herdam os atributos comuns. No relacional, mapeamos com tabela
  separada por especialização + FK UNIQUE (garante o 1:1).
- **Tabela de domínio (lookup)**: DIA_SEMANA evita gravar o texto "Segunda-feira"
  repetido em todo lugar — grava-se o id, o nome existe uma vez só.

## 2.3 Mapeamento DER → relacional (as regras que aplicamos)

1. **Entidade → tabela**; atributos → colunas; identificador → chave primária.
2. **1:N** → chave estrangeira no lado N (disciplina recebe id_periodo).
3. **N:M** → tabela nova com as duas FKs formando chave composta (professor_disciplina).
4. **1:1 (especialização)** → tabela própria com FK UNIQUE para a tabela geral.
5. **Relacionamento com atributos / grau > 2** → entidade associativa (alocacao).

## 2.4 Normalização (o que dizer se pedirem para provar)

- **1FN — atomicidade**: nenhuma coluna guarda lista, vetor ou texto composto.
  *Contraexemplo que evitamos*: uma coluna "horarios" com o texto "SEG-19h;QUA-19h".
- **2FN — sem dependência parcial**: vale para chaves compostas. Um atributo não pode
  depender de só uma parte da chave. Nossa única chave composta (professor_disciplina)
  não tem atributos extras → 2FN automática.
  *Contraexemplo*: se professor_disciplina tivesse "nome_professor", ele dependeria só
  de id_professor (metade da chave).
- **3FN — sem dependência transitiva**: atributo não-chave não pode depender de outro
  atributo não-chave. *Contraexemplo que evitamos*: colocar "nome_professor" em
  alocacao — ele depende de id_professor, que não é a chave da tabela.
- **Por que normalizar?** Evita redundância e as três anomalias: de **inserção** (não
  consigo cadastrar X sem inventar Y), de **atualização** (mudar um nome em 20 lugares)
  e de **exclusão** (apagar a última aula do professor apaga o cadastro dele junto).

## 2.5 Chaves e constraints (vocabulário preciso)

- **Chave primária (PK)**: identifica unicamente a linha; não aceita NULL; uma por tabela.
- **Chave estrangeira (FK)**: referencia a PK de outra tabela; é o que garante
  **integridade referencial** — não existe alocação de uma disciplina que não existe.
- **UNIQUE**: impede duplicata em coluna(s) que não são a PK. É a nossa principal
  ferramenta de regra de negócio (3 UNIQUEs em alocacao).
- **CHECK**: valida a própria linha (slot IN (1,2), carga_horaria > 0).
- **IDENTITY**: gera o id automaticamente (auto-incremento do SQL Server).
- **Limite das constraints**: só enxergam a própria tabela/linha. Regra que precisa
  de JOIN → **trigger**.

## 2.6 Triggers

- Procedimento que o SGBD executa automaticamente em INSERT/UPDATE/DELETE.
- No SQL Server, `AFTER INSERT` roda depois da modificação, dentro da mesma transação;
  a tabela virtual `inserted` contém as linhas novas.
- Se a regra for violada: `RAISERROR` + `ROLLBACK TRANSACTION` → tudo desfeito.
- Usamos dois: choque de período no mesmo horário; professor sem habilitação.
- **Defesa em profundidade**: aplicação valida (boa UX) E banco valida (integridade
  garantida até contra INSERT manual no SSMS).

## 2.7 SQL — o que cada grupo de consulta exercita

**Junção (JOIN)**: combina linhas de tabelas pela igualdade de chaves. INNER JOIN só
traz quem tem correspondência; **LEFT JOIN** traz todos da esquerda mesmo sem match
(usamos na vw_carga_professores para professor com turma sem alunos aparecer com 0).

**Operações de conjuntos** (comparam resultados inteiros, linha a linha):
- `UNION` — junta e **remove duplicatas** (UNION ALL manteria);
- `INTERSECT` — só o que está nos dois;
- `EXCEPT` — o que está no primeiro e não no segundo.
- Exigem mesmo número e tipos compatíveis de colunas nos dois SELECTs.

**Agregação**: SUM, COUNT, MAX, MIN, AVG resumem grupos de linhas.
- `GROUP BY` define os grupos; sem ele, a agregação é sobre tudo.
- `WHERE` filtra **linhas antes** de agrupar; `HAVING` filtra **grupos depois** —
  só HAVING pode usar agregação (`HAVING COUNT(*) >= 2`).

**Operadores de filtro**:
- `LIKE '%Dados%'` — busca por padrão (% = qualquer sequência, _ = um caractere);
- `BETWEEN a AND b` — intervalo inclusivo nas duas pontas;
- `IN (x, y)` — pertence à lista; equivale a ORs encadeados.

**Visão (VIEW)**: consulta nomeada e armazenada; não duplica dados — é expandida na
hora da consulta. Vantagens: reuso (a junção de 9 tabelas escrita uma vez), abstração
(a aplicação nem conhece as tabelas base) e segurança (dá-se permissão na view).

## 2.8 O algoritmo (teoria mínima de grafos)

- **Grafo**: vértices + arestas. **Grafo de conflitos**: aresta = "não podem coexistir".
- **Coloração própria**: atribuir cores aos vértices sem que vizinhos repitam cor.
  Aqui, cor = horário → coloração válida = grade sem choques.
- **Número cromático**: mínimo de cores possível. Calculá-lo é **NP-difícil** — não
  existe algoritmo eficiente conhecido para o caso geral; força bruta seria 10^20
  combinações para 20 disciplinas e 10 cores.
- **Heurística gulosa (Welsh-Powell)**: ordena vértices por grau decrescente (quem tem
  mais conflitos escolhe primeiro) e dá a cada um a menor cor livre. O(V²). Não garante
  o mínimo, mas costuma chegar perto.
- **Clique**: subconjunto de vértices todos ligados entre si. Uma clique de tamanho k
  exige pelo menos k cores → é um **limite inferior**. Nosso grafo tem cliques de 5
  (4 disciplinas de um período + professor compartilhado com outro período), e usamos
  5 cores → **ótimo comprovado para esta instância**.
- **Por que atribuir professores antes de colorir?** As arestas "mesmo professor"
  dependem dessa atribuição. Distribuindo a carga (professor menos carregado primeiro,
  disciplinas mais restritas primeiro), criamos menos arestas → grafo mais fácil de
  colorir com poucas cores.

## 2.9 A aplicação (o que pode ser perguntado)

- **pyodbc**: biblioteca Python que fala com o SQL Server via driver ODBC, usando uma
  connection string (servidor, banco, credenciais).
- **Consulta parametrizada**: `cursor.execute('... WHERE login = ?', (login,))` — o
  valor viaja separado do SQL, impossibilitando SQL Injection. Nunca concatenamos string.
- **Transação**: a geração da grade faz DELETE da grade antiga + 20 INSERTs e só então
  `commit()`. Se qualquer INSERT falhar, nada é aplicado (**atomicidade**, o A do ACID).
- **Sessão Flask**: depois do login, o id do usuário fica na sessão; um decorator
  verifica a sessão antes de cada rota protegida.
- **Senha sem hash**: dispensado pela especificação; em produção seria bcrypt/argon2.

---

# Últimos conselhos contra o nervosismo

1. **Você construiu a resposta de quase toda pergunta possível.** As perguntas do
   professor quase sempre serão "por quê?" — e cada decisão do projeto tem um porquê
   registrado neste documento.
2. **Se travar num slide**, leia a ideia-chave em negrito e improvise em volta dela.
   Ninguém percebe.
3. **Se não souber uma resposta**, diga: "essa situação a gente não tratou no escopo,
   mas o caminho seria..." — e conecte com algo que você sabe (trigger, constraint,
   consulta). Honestidade com raciocínio vale mais que enrolação.
4. **Ensaie em voz alta uma vez cronometrando.** É o que mais aumenta a segurança.
5. A demo e o INSERT inválido no SSMS (no guia de preparação) são seus trunfos:
   mostrar o banco rejeitando um conflito ao vivo prova domínio do conteúdo.
