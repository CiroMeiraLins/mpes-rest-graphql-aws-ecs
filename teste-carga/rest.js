import http from 'k6/http';
import { check } from 'k6';
import { options as opcoesCompartilhadas, proximaOperacao, latenciaOperacao, PAGE_LIMIT } from './config.js';

export const options = opcoesCompartilhadas;

const BASE_URL = __ENV.BASE_URL || 'http://0.0.0.0:8000';
const HEADERS = { 'Content-Type': 'application/json' };

// GET com tags de cenário; "name" agrupa as URLs com id/offset variáveis
function get(url, cenario, nome) {
  return http.get(url, { headers: HEADERS, tags: { cenario, name: nome } });
}

function simples(id) {
  const r = get(`${BASE_URL}/registros/${id}`, 'simples', 'GET /registros/{id}');
  check(r, {
    'simples: status 200': (x) => x.status === 200,
    'simples: registro correto': (x) => x.status === 200 && x.json('id') === id,
  }, { cenario: 'simples' });
  latenciaOperacao.add(r.timings.duration, { cenario: 'simples' });
}

// REST: objeto composto (cadastro + endereco + preferencias) em uma única requisição
function composto(id) {
  const r = get(`${BASE_URL}/registros/${id}/detalhes`, 'composto', 'GET /registros/{id}/detalhes');

  check(r, {
    'composto: status 200': (x) => x.status === 200,
    'composto: objeto composto completo': (x) => {
      if (x.status !== 200) return false;
      const b = x.json();
      return b.id === id && 'endereco' in b && 'preferencias' in b;
    },
  }, { cenario: 'composto' });

  latenciaOperacao.add(r.timings.duration, { cenario: 'composto' });
}

function complexo(offset) {
  const r = get(`${BASE_URL}/registros?limit=${PAGE_LIMIT}&offset=${offset}`, 'complexo', 'GET /registros');
  check(r, {
    'complexo: status 200': (x) => x.status === 200,
    'complexo: página completa': (x) => x.status === 200 && x.json('items.#') === PAGE_LIMIT,
  }, { cenario: 'complexo' });
  latenciaOperacao.add(r.timings.duration, { cenario: 'complexo' });
}

export default function () {
  const { cenario, id, offset } = proximaOperacao();
  if (cenario === 'simples') simples(id);
  else if (cenario === 'composto') composto(id);
  else complexo(offset);
}
