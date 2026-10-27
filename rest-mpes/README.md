# API REST — Flask + SQLAlchemy + PostgreSQL

API **REST** do experimento, com **Flask**, **SQLAlchemy** e **PostgreSQL** (Amazon Aurora/RDS),
empacotada com **Docker** e servida pelo **gunicorn** na porta **8000**.

Usa a tabela `api_experimento.registros` (ver `../banco_de_dados/`), a mesma da API GraphQL.

## Endpoints

| Método e rota | Cenário | Retorno |
|---|---|---|
| `GET /health` | — | `{"status": "ok"}` |
| `GET /registros/{id}` | Simples | Dados cadastrais do registro |
| `GET /registros/{id}/detalhes` | Composto | Dados cadastrais + `endereco` + `preferencias` |
| `GET /registros?limit=50&offset=0` | Complexo | Página de registros completos + `total`, `limit`, `offset` (`limit` entre 1 e 100) |
| `GET /registros/{id}/endereco` | — | Só o endereço (sub-recurso; não usado no teste de carga) |
| `GET /registros/{id}/preferencias` | — | Só as preferências (sub-recurso; não usado no teste de carga) |

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
   curl http://localhost:8000/health
   curl http://localhost:8000/registros/<id>
   curl http://localhost:8000/registros/<id>/detalhes
   curl "http://localhost:8000/registros?limit=50&offset=0"
   ```

## Observações

- O gunicorn roda com 2 workers e 4 threads (ver `Dockerfile`).
- A criação automática da tabela em `app.py` é apenas para desenvolvimento; o banco do experimento
  é criado pelos scripts de `../banco_de_dados/`.
