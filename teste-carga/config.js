// Configuração COMPARTILHADA pelos scripts rest.js e graphql.js.
// Garante que os dois tratamentos recebam exatamente a mesma carga:
// mesmos VUs, mesmas iterações, mesma sequência de cenários, IDs e páginas.

import { SharedArray } from 'k6/data';
import exec from 'k6/execution';
import { Trend } from 'k6/metrics';

export const CENARIOS = ['simples', 'composto', 'complexo'];

// Opcional: rodar um único cenário  ->  k6 run -e CENARIO=simples rest.js
const cenarioUnico = __ENV.CENARIO;
if (cenarioUnico && !CENARIOS.includes(cenarioUnico)) {
  throw new Error(`CENARIO inválido: ${cenarioUnico}. Use: ${CENARIOS.join(', ')}`);
}
const ATIVOS = cenarioUnico ? [cenarioUnico] : CENARIOS;

export const VUS = 10;

// Quantidade de operações por cenário (total = 1000).
// Podem ser alteradas com -e QTD_SIMPLES=... -e QTD_COMPOSTO=... -e QTD_COMPLEXO=...
export const QUANTIDADES = {
  simples: parseInt(__ENV.QTD_SIMPLES || '333', 10),
  composto: parseInt(__ENV.QTD_COMPOSTO || '333', 10),
  complexo: parseInt(__ENV.QTD_COMPLEXO || '334', 10),
};

export const PAGE_LIMIT = 50; // tamanho da página do cenário complexo

// IDs reais da tabela registros (gerados uma vez; ver README.md)
export const IDS = new SharedArray('ids', () => JSON.parse(open('./ids.json')));

// Latência da OPERAÇÃO funcional. Em todos os cenários, cada operação
// corresponde a uma única requisição HTTP nas duas APIs.
export const latenciaOperacao = new Trend('latencia_operacao', true);

// Plano determinístico de execução: alterna simples -> composto -> complexo
// enquanto cada cenário ainda tiver operações a executar.
// Com 333/333/334, a última iteração (a 1000ª) é a operação complexa extra.
// Cada item do plano é [cenario, n], onde n é a n-ésima operação daquele cenário.
const PLANO = [];
{
  const executadas = { simples: 0, composto: 0, complexo: 0 };
  const total = ATIVOS.reduce((soma, c) => soma + QUANTIDADES[c], 0);
  while (PLANO.length < total) {
    for (const c of ATIVOS) {
      if (executadas[c] < QUANTIDADES[c]) {
        PLANO.push([c, executadas[c]]);
        executadas[c] += 1;
      }
    }
  }
}

// Thresholds "sempre verdadeiros" apenas para forçar o k6 a exibir/exportar
// as submétricas por cenário (p50, p90, p95, p99 de cada um).
const thresholds = {};
for (const c of ATIVOS) {
  thresholds[`latencia_operacao{cenario:${c}}`] = ['p(99)>=0'];
  thresholds[`http_req_duration{cenario:${c}}`] = ['p(99)>=0'];
  thresholds[`http_reqs{cenario:${c}}`] = ['count>=0'];
  thresholds[`http_req_failed{cenario:${c}}`] = ['rate>=0'];
  thresholds[`checks{cenario:${c}}`] = ['rate>=0'];
}

export const options = {
  scenarios: {
    carga_mista: {
      executor: 'shared-iterations',
      vus: VUS,
      iterations: PLANO.length, // 333 + 333 + 334 = 1000
      maxDuration: '60m',
    },
  },
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
  thresholds,
};

// Define, de forma determinística, o que cada iteração executa.
export function proximaOperacao() {
  const [cenario, n] = PLANO[exec.scenario.iterationInTest];

  // Passo primo para espalhar os IDs pela tabela sem repetir
  const id = IDS[(n * 7919) % IDS.length];

  // Páginas completas distribuídas pela tabela
  const totalPaginas = Math.floor(IDS.length / PAGE_LIMIT);
  const offset = ((n * 37) % totalPaginas) * PAGE_LIMIT;

  return { cenario, id, offset };
}