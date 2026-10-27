# API GraphQL — Flask + Ariadne + SQLAlchemy + PostgreSQL

API **GraphQL** do experimento, com **Flask**, **Ariadne**, **SQLAlchemy** e **PostgreSQL** (Amazon Aurora/RDS),
empacotada com **Docker** e servida pelo **gunicorn** na porta **8001**, em `POST /graphql`.

Usa a tabela `api_experimento.registros` (ver `../banco_de_dados/`), a mesma da API REST.

## Consultas

| Consulta | Cenário | Retorno |
|---|---|---|
| `registro(id)` com os campos cadastrais | Simples | Mesmos campos de `GET /registros/{id}` |
| `registro(id)` com os campos cadastrais + `endereco` + `preferencias` | Composto | Mesmos campos de `GET /registros/{id}/detalhes` |
| `registros(limit, offset)` | Complexo | Página de registros + `total`, `limit`, `offset` (`limit` entre 1 e 100) |

## Como executar

1. Crie um arquivo `.env` nesta pasta:
   ```bash
   DATABASE_URL=postgresql+psycopg://usuario:senha@host:5432/banco?sslmode=require
   # Opcionais (valores padrão):
   # DB_POOL_SIZE=5
   # DB_MAX_OVERFLOW=10
   # DB_POOL_RECYCLE=1800
   ```
2. Suba o serviço:
   ```bash
   docker compose up --build -d
   ```
3. Teste:
   ```bash
   curl http://localhost:8001/health

   curl -X POST http://localhost:8001/graphql \
     -H "Content-Type: application/json" \
     -d '{"query":"query ($id: ID!) { registro(id: $id) { id nome email endereco preferencias } }","variables":{"id":"<id>"}}'

   curl -X POST http://localhost:8001/graphql \
     -H "Content-Type: application/json" \
     -d '{"query":"{ registros(limit: 50, offset: 0) { total limit offset items { id nome } } }"}'
   ```

## Observações

- O gunicorn roda com 2 workers e 4 threads (ver `Dockerfile`).
- A API não expõe mutations; o experimento avalia apenas consultas.
- A criação automática da tabela em `app.py` é apenas para desenvolvimento; o banco do experimento
  é criado pelos scripts de `../banco_de_dados/`.
