#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="${SCRIPT_DIR}/results-fixed"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

TOTAL_ITERATIONS="${TOTAL_ITERATIONS:-1000}"
VU_TARGET="${VU_TARGET:-10}"
APP_URL="${APP_URL:-http://localhost:8080}"
TEST_TYPE="${TEST_TYPE:-cpu}"

mkdir -p "${RESULTS_DIR}"

OUTPUT_RAW_CSV="${RESULTS_DIR}/${TEST_TYPE}-${VU_TARGET}vus-${TOTAL_ITERATIONS}reqs-${TIMESTAMP}-raw.csv"
OUTPUT_REQUESTS_CSV="${RESULTS_DIR}/${TEST_TYPE}-${VU_TARGET}vus-${TOTAL_ITERATIONS}reqs-${TIMESTAMP}-requests.csv"
OUTPUT_SUMMARY_JSON="${RESULTS_DIR}/${TEST_TYPE}-${VU_TARGET}vus-${TOTAL_ITERATIONS}reqs-${TIMESTAMP}-summary.json"
OUTPUT_LOG="${RESULTS_DIR}/${TEST_TYPE}-${VU_TARGET}vus-${TOTAL_ITERATIONS}reqs-${TIMESTAMP}.log"

if [ "${TEST_TYPE}" = "cpu" ]; then
    SCRIPT_FILE="${SCRIPT_DIR}/cpu-bound-fixed-test.js"
elif [ "${TEST_TYPE}" = "io" ]; then
    SCRIPT_FILE="${SCRIPT_DIR}/io-bound-fixed-test.js"
else
    echo "ERRO: TEST_TYPE deve ser 'cpu' ou 'io' (recebido: ${TEST_TYPE})"
    exit 1
fi

if [ ! -f "${SCRIPT_FILE}" ]; then
    echo "ERRO: script k6 não encontrado: ${SCRIPT_FILE}"
    exit 1
fi

echo "==================================================="
echo "Teste de carga com iterações fixas"
echo "==================================================="
echo "Tipo:           ${TEST_TYPE}"
echo "URL:            ${APP_URL}"
echo "VUs:            ${VU_TARGET}"
echo "Iterações:      ${TOTAL_ITERATIONS}"
echo "Timestamp:      ${TIMESTAMP}"
echo "==================================================="
echo

k6 run \
    -e APP_URL="${APP_URL}" \
    -e VU_TARGET="${VU_TARGET}" \
    -e TOTAL_ITERATIONS="${TOTAL_ITERATIONS}" \
    --out csv="${OUTPUT_RAW_CSV}" \
    --summary-export "${OUTPUT_SUMMARY_JSON}" \
    "${SCRIPT_FILE}" \
    | tee "${OUTPUT_LOG}"

echo
echo "==================================================="
echo "Processando CSV para formato final (1 linha por requisição)..."
echo "==================================================="

python3 "${SCRIPT_DIR}/csv_per_request.py" \
    "${OUTPUT_RAW_CSV}" \
    "${OUTPUT_REQUESTS_CSV}"

echo
echo "Arquivos gerados:"
echo "  Raw CSV (k6 nativo):       ${OUTPUT_RAW_CSV}"
echo "  CSV por requisição:        ${OUTPUT_REQUESTS_CSV}"
echo "  Summary JSON:              ${OUTPUT_SUMMARY_JSON}"
echo "  Log:                       ${OUTPUT_LOG}"
