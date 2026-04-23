#!/usr/bin/env bash
set -euo pipefail

RESULTS_DIR="${HOME}/k6-tests/results"
DATE_TAG="rerun_$(date +%Y%m%d_%H%M%S)"

mkdir -p "${RESULTS_DIR}/${DATE_TAG}"

MVC_URL="http://52.12.185.217:8080"
WEBFLUX_URL="http://52.12.185.217:8081"

# Configurações com CV > 20% identificadas pela análise estatística (mvc-io-250 e mvc-io-400 nas métricas p99)
PROBLEMATIC_CONFIGS=(
  "mvc:${MVC_URL}:io:250"
  "mvc:${MVC_URL}:io:400"
)

REPEATS=3

run_test_with_raw() {
  local app_name="$1"
  local app_url="$2"
  local workload="$3"
  local vus="$4"
  local repeat="$5"

  local steady="3m"
  if [ "$vus" -gt 250 ]; then
    steady="5m"
  fi

  local script_file=""
  if [ "$workload" = "cpu" ]; then
    script_file="cpu-bound-test.js"
  else
    script_file="io-bound-test.js"
  fi

  local out_summary="${RESULTS_DIR}/${DATE_TAG}/${app_name}-${workload}-${vus}-run${repeat}.json"
  local out_raw="${RESULTS_DIR}/${DATE_TAG}/${app_name}-${workload}-${vus}-run${repeat}-raw.json"
  local out_txt="${RESULTS_DIR}/${DATE_TAG}/${app_name}-${workload}-${vus}-run${repeat}.log"

  echo "===================================================="
  echo "Re-running: app=${app_name} workload=${workload} vus=${vus} repeat=${repeat}"
  echo "URL: ${app_url}"
  echo "Steady duration: ${steady}"
  echo "Output summary: ${out_summary}"
  echo "Output raw NDJSON: ${out_raw}"
  echo "===================================================="

  k6 run \
    -e APP_URL="${app_url}" \
    -e VU_TARGET="${vus}" \
    -e STEADY_DURATION="${steady}" \
    "${script_file}" \
    --summary-export "${out_summary}" \
    --out json="${out_raw}" \
    | tee "${out_txt}"

  echo "Finished: app=${app_name} workload=${workload} vus=${vus} repeat=${repeat}"
}

warmup() {
  local app_url="$1"
  echo "Warming up ${app_url} ..."
  k6 run -e APP_URL="${app_url}" -e VU_TARGET=20 -e STEADY_DURATION=2m io-bound-test.js >/dev/null
}

main() {
  echo "===================================================="
  echo "Re-execução das configurações problemáticas (CV > 20%)"
  echo "Modo: NDJSON raw para permitir filtragem do ramp-up"
  echo "===================================================="

  warmup "${MVC_URL}"

  for repeat in $(seq 1 ${REPEATS}); do
    for config in "${PROBLEMATIC_CONFIGS[@]}"; do
      IFS=':' read -r app_name app_url workload vus <<< "${config}"
      run_test_with_raw "${app_name}" "${app_url}" "${workload}" "${vus}" "${repeat}"
      sleep 60
    done
  done

  echo "===================================================="
  echo "Re-execução finalizada."
  echo "Resultados em: ${RESULTS_DIR}/${DATE_TAG}"
  echo ""
  echo "Próximo passo: rodar analise_ndjson.py para filtrar o ramp-up."
  echo "===================================================="
}

main
