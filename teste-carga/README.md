# Testes de carga (k6) — cenários simples, composto e complexo

Os scripts `rest.js` e `graphql.js` usam a mesma configuração (`config.js`):
10 VUs, carga mista com 1000 operações em todos os cenários,
na mesma sequência de IDs e páginas para os dois tratamentos.
Em todos os cenários, cada operação corresponde a **uma única requisição HTTP** nas duas APIs
(1000 requisições por rodada em cada tratamento).

| Cenário  | REST                                                                 | GraphQL                                   |
|----------|----------------------------------------------------------------------|-------------------------------------------|
| Simples  | `GET /registros/{id}` (dados cadastrais)                             | `registro(id)` com os mesmos campos       |
| Composto | `GET /registros/{id}/detalhes` (cadastro + `endereco` + `preferencias`) | `registro(id)` + `endereco` + `preferencias` |
| Complexo | `GET /registros?limit=50&offset=N` (registros completos + `total`)   | `registros(limit:50, offset:N)` com os mesmos campos |

## 1. Gerar `ids.json` (uma única vez, antes da primeira rodada)

```bash
psql "$DATABASE_URL" -At \
  -c "select json_agg(id order by id) from api_experimento.registros" > ids.json
```

O mesmo arquivo deve ser usado por todas as rodadas de REST e GraphQL.

## 2. Executar uma rodada

```bash
mkdir -p 20260729
k6 run --summary-export=20260729/rest.json    rest.js
k6 run --summary-export=20260729/graphql.json graphql.js
```

## 3. Métricas por cenário no JSON exportado

- `http_req_duration{cenario:X}` — duração de cada requisição HTTP. **Métrica principal de comparação.**
- `latencia_operacao{cenario:X}` — latência da operação funcional; como cada operação
  é uma única requisição, coincide com `http_req_duration`.
- `http_reqs{cenario:X}` — número de requisições e throughput (requisições/s).
- `http_req_failed{cenario:X}` e `checks{cenario:X}` — erros e validações.

Cada métrica traz avg, min, med (p50), max, p(90), p(95) e p(99).
Os thresholds em `config.js` existem só para forçar a exportação dessas submétricas;
o `false`/`true` exibido neles não tem significado.
