# Trabalho Final — Banco de Dados 1/2026
## Sistema de Gestão de Horários de Disciplinas (ADS / PUC Minas)

## Estrutura do projeto

```
TrabalhoBD/
├── sql/
│   ├── 01_ddl.sql            # CREATE DATABASE, 13 CREATE TABLE, 2 triggers
│   ├── 02_inserts.sql        # carga de dados de teste (inclui grade gerada)
│   ├── 03_consultas.sql      # 12 consultas exigidas, com explicações
│   └── 04_views.sql          # 2 visões (grade e carga docente)
├── aplicacao/
│   ├── app.py                # aplicação web Flask (4 funcionalidades)
│   ├── db.py                 # conexão SQL Server (pyodbc)
│   ├── alocador.py           # algoritmo de alocação (coloração de grafos)
│   ├── teste_alocador.py     # teste do algoritmo
│   ├── teste_consultas.py    # teste das 14 consultas/visões
│   ├── teste_app_offline.py  # teste do SQL e templates da aplicação
│   ├── requirements.txt
│   └── templates/            # páginas HTML (Jinja2)
├── documentacao/
│   ├── DER.png               # diagrama entidade-relacionamento
│   ├── DiagramaClasses.png   # diagrama de classes UML
│   └── Trabalho_Final_BD.docx# documento final
└── scripts_diagramas/        # geradores dos diagramas (graphviz)
```

## Como executar

1. **Banco de dados (SQL Server):** execute, nesta ordem, no SSMS:
   `01_ddl.sql` → `02_inserts.sql` → `04_views.sql`.
   As consultas de `03_consultas.sql` podem ser executadas individualmente.

2. **Aplicação web:**
   ```
   cd aplicacao
   pip install -r requirements.txt
   ```
   Ajuste `SERVER`/`DRIVER` em `db.py` conforme sua instância e rode:
   ```
   python app.py
   ```
   Acesse http://localhost:5000 — login de teste: `carlos` / `123456` (coordenador).

3. **Testes:** `python teste_alocador.py` e `python teste_consultas.py`
   (este usa SQLite apenas para validar a lógica das consultas).

## Funcionalidades da aplicação

1. Cadastro de usuários (validação no código da aplicação)
2. Autenticação de usuários (sessão Flask)
3. Gestão de habilitações professor × disciplina
4. Geração automática da grade (algoritmo de coloração de grafos) e visualização

Regras de negócio críticas também são garantidas no SGBD por constraints
UNIQUE e pelos triggers `trg_valida_periodo_horario` e `trg_valida_habilitacao`.
