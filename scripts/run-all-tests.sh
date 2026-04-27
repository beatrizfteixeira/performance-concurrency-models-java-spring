#!/usr/bin/env bash
set -euo pipefail

RESULTS_DIR="${HOME}/k6-tests/results"
DATE_TAG="$(date +%Y%m%d_%H%M%S)"

mkdir -p "${RESULTS_DIR}/${DATE_TAG}"

MVC_URL="http://44.255.83.113:8080"
WEBFLUX_URL="http://44.255.83.113:8081"

CPU_VUS=(5)
TOTAL_ITERATIONS=500
WARMUP_DURATION="5s"

REPEATS=1
SLEEP_BETWEEN=60

extract_steady_csv() {
  local raw_csv="$1"
  local steady_csv="$2"

  echo "timestamp,duration_ms" > "${steady_csv}"
  awk -F',' '$1 == "http_req_duration" && $12 == "steady" { print $2 "," $3 }' \
    "${raw_csv}" >> "${steady_csv}"

  local count
  count=$(( $(wc -l < "${steady_csv}") - 1 ))
  echo "  -> ${steady_csv}: ${count} requests extraidas"

  rm -f "${raw_csv}"
}

run_test() {
  local app_name="$1"
  local app_url="$2"
  local workload="$3"
  local vus="$4"
  local repeat="$5"

  local script_file=""
  if [ "${workload}" = "cpu" ]; then
    script_file="cpu-bound-test.js"
  else
    echo "ERRO: workload nao suportado nesta versao: ${workload}"
    exit 1
  fi

  local prefix="${RESULTS_DIR}/${DATE_TAG}/${app_name}-${workload}-${vus}vus-${TOTAL_ITERATIONS}iter-run${repeat}"
  local out_summary="${prefix}-summary.json"
  local out_raw="${prefix}-raw.csv"
  local out_steady="${prefix}-steady.csv"
  local out_log="${prefix}.log"

  echo "===================================================="
  echo "Running: app=${app_name} workload=${workload} vus=${vus} iterations=${TOTAL_ITERATIONS} repeat=${repeat}"
  echo "URL: ${app_url}"
  echo "Warmup: ${WARMUP_DURATION} | Iterations: ${TOTAL_ITERATIONS}"
  echo "===================================================="

  k6 run \
    -e APP_URL="${app_url}" \
    -e VU_TARGET="${vus}" \
    -e TOTAL_ITERATIONS="${TOTAL_ITERATIONS}" \
    -e WARMUP_DURATION="${WARMUP_DURATION}" \
    "${script_file}" \
    --summary-export "${out_summary}" \
    --out csv="${out_raw}" \
    | tee "${out_log}"

  extract_steady_csv "${out_raw}" "${out_steady}"

  echo "Finished: app=${app_name} workload=${workload} vus=${vus} repeat=${repeat}"
}

smoke_test() {
  echo "Running smoke test on ${MVC_URL}..."

  k6 run \
    -e APP_URL="${MVC_URL}" \
    -e VU_TARGET=2 \
    -e TOTAL_ITERATIONS=20 \
    -e WARMUP_DURATION=2s \
    cpu-bound-test.js >/dev/null

  echo "Smoke test on MVC passed."

  # echo "Running smoke test on ${WEBFLUX_URL}..."

  # k6 run \
  #   -e APP_URL="${WEBFLUX_URL}" \
  #   -e VU_TARGET=2 \
  #   -e TOTAL_ITERATIONS=20 \
  #   -e WARMUP_DURATION=2s \
  #   cpu-bound-test.js >/dev/null

  # echo "Smoke test on WebFlux passed."
}

main() {
  smoke_test

  for repeat in $(seq 1 ${REPEATS}); do
    for vus in "${CPU_VUS[@]}"; do
      run_test "mvc" "${MVC_URL}" "cpu" "${vus}" "${repeat}"

      # run_test "webflux" "${WEBFLUX_URL}" "cpu" "${vus}" "${repeat}"

      # if [ "${repeat}" -lt "${REPEATS}" ] || [ "${vus}" != "${CPU_VUS[-1]}" ]; then
      #   echo "Sleeping ${SLEEP_BETWEEN}s before next run..."
      #   sleep "${SLEEP_BETWEEN}"
      # fi
    done
  done

  echo "===================================================="
  echo "All tests finished."
  echo "Results stored in: ${RESULTS_DIR}/${DATE_TAG}"
  echo "===================================================="
  ls -lh "${RESULTS_DIR}/${DATE_TAG}"
}

main
