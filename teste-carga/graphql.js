import http from 'k6/http';
import { check } from 'k6';
import { options as opcoesCompartilhadas, proximaOperacao, latenciaOperacao, PAGE_LIMIT } from './config.js';

export const options = opcoesCompartilhadas;

const URL = __ENV.GRAPHQL_URL || 'http://0.0.0.0:8001/graphql';
const HEADERS = { 'Content-Type': 'application/json' };

// Mesmos campos devolvidos por GET /registros/{id} na API REST
const CAMPOS_CADASTRO = `
  id nome email idade ativo criado_em atualizado_em
  salario score_credito descricao status tags
  empresa_id latitude longitude
`;

// Payloads equivalentes aos da API REST em cada cenário
const QUERY_SIMPLES = `
  query Simples($id: ID!) {
    registro(id: $id) { ${CAMPOS_CADASTRO} }
  }`;

// Equivale a GET /registros/{id}/detalhes (registro + endereco + preferencias)
const QUERY_COMPOSTO = `
  query Composto($id: ID!) {
    registro(id: $id) { ${CAMPOS_CADASTRO} endereco preferencias }
  }`;

// Equivale a GET /registros?limit=&offset=
const QUERY_COMPLEXO = `
  query Complexo($limit: Int!, $offset: Int!) {
    registros(limit: $limit, offset: $offset) {
      total limit offset
      items { ${CAMPOS_CADASTRO} endereco preferencias }
    }
  }`;

function post(query, variables, cenario) {
  return http.post(URL, JSON.stringify({ query, variables }), {
    headers: HEADERS,
    tags: { cenario, name: `POST /graphql (${cenario})` },
  });
}

const semErros = (r) => r.status === 200 && !r.json('errors');

function simples(id) {
  const r = post(QUERY_SIMPLES, { id }, 'simples');
  check(r, {
    'simples: status 200': (x) => x.status === 200,
    'simples: registro correto': (x) => semErros(x) && x.json('data.registro.id') === id,
  }, { cenario: 'simples' });
  latenciaOperacao.add(r.timings.duration, { cenario: 'simples' });
}

function composto(id) {
  const r = post(QUERY_COMPOSTO, { id }, 'composto');
  check(r, {
    'composto: status 200': (x) => x.status === 200,
    'composto: objeto composto completo': (x) => semErros(x) && x.json('data.registro.id') === id,
  }, { cenario: 'composto' });
  latenciaOperacao.add(r.timings.duration, { cenario: 'composto' });
}

function complexo(offset) {
  const r = post(QUERY_COMPLEXO, { limit: PAGE_LIMIT, offset }, 'complexo');
  check(r, {
    'complexo: status 200': (x) => x.status === 200,
    'complexo: página completa': (x) => semErros(x) && x.json('data.registros.items.#') === PAGE_LIMIT,
  }, { cenario: 'complexo' });
  latenciaOperacao.add(r.timings.duration, { cenario: 'complexo' });
}

export default function () {
  const { cenario, id, offset } = proximaOperacao();
  if (cenario === 'simples') simples(id);
  else if (cenario === 'composto') composto(id);
  else complexo(offset);
}
