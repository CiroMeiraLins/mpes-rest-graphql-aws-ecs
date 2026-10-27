# REST × GraphQL na AWS — artefatos da dissertação

Código-fonte, scripts de banco de dados e scripts de teste de carga da dissertação
**"Impacto financeiro e computacional na escolha entre REST e GraphQL na nuvem AWS"**
(Mestrado Profissional em Engenharia de Software — CESAR School, 2026).

Autor: Ciro Buregio de Meira Lins · Orientador: Prof. Julio Venâncio de Menezes Júnior

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `banco_de_dados/` | `create.sql` (schema `api_experimento` e tabela `registros`) e `insert.sql` (20.000 registros sintéticos) |
| `rest-mpes/` | API REST (Python 3.12, Flask, SQLAlchemy, gunicorn) — porta 8000 |
| `graphql-mpes/` | API GraphQL (Python 3.12, Flask, Ariadne, SQLAlchemy, gunicorn) — porta 8001 |
| `teste-carga/` | Scripts k6 com a carga mista dos cenários simples, composto e complexo |

As duas APIs usam a mesma tabela, a mesma stack e as mesmas versões de bibliotecas, e devolvem
os mesmos campos em cada cenário. Em todos os cenários, cada operação é uma única requisição HTTP.

## Como reproduzir

1. **Banco de dados** (PostgreSQL 13 ou superior):
   ```bash
   psql "$DATABASE_URL" -f banco_de_dados/create.sql
   psql "$DATABASE_URL" -f banco_de_dados/insert.sql
   ```
2. **APIs**: siga o README de cada pasta (`rest-mpes/` e `graphql-mpes/`).
3. **Teste de carga**: siga `teste-carga/README.md` (gerar `ids.json` e executar `rest.js` e `graphql.js`).

## Ambiente do experimento

Amazon ECS (Fargate) na região us-west-2, com 4 vCPUs e 8 GiB por tarefa, e banco PostgreSQL
no Amazon Aurora. A infraestrutura foi configurada pelo console da AWS, com a mesma configuração
para as duas APIs.
