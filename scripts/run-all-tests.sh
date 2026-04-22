#!/usr/bin/env bash
set -euo pipefail

RESULTS_DIR="${HOME}/k6-tests/results"
DATE_TAG="$(date +%Y%m%d_%H%M%S)"

mkdir -p "${RESULTS_DIR}/${DATE_TAG}"

# Ajuste os IPs conforme sua infra
MVC_URL="http://18.236.90.11:8080"
WEBFLUX_URL="http://18.236.90.11:8081"

# Níveis de carga
CPU_VUS=(10 20 30 40 50 75 100)
IO_VUS=(50 100 150 200 250 300 400 500 600 800)

# Repetições
REPEATS=3

run_test() {
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

  local out_json="${RESULTS_DIR}/${DATE_TAG}/${app_name}-${workload}-${vus}-run${repeat}.json"
  local out_txt="${RESULTS_DIR}/${DATE_TAG}/${app_name}-${workload}-${vus}-run${repeat}.log"

  echo "===================================================="
  echo "Running: app=${app_name} workload=${workload} vus=${vus} repeat=${repeat}"
  echo "URL: ${app_url}"
  echo "Steady duration: ${steady}"
  echo "Output JSON: ${out_json}"
  echo "===================================================="

  k6 run \
    -e APP_URL="${app_url}" \
    -e VU_TARGET="${vus}" \
    -e STEADY_DURATION="${steady}" \
    "${script_file}" \
    --summary-export "${out_json}" \
    | tee "${out_txt}"

  echo "Finished: app=${app_name} workload=${workload} vus=${vus} repeat=${repeat}"
}

smoke_test() {
  echo "Running smoke tests..."

  k6 run -e APP_URL="${MVC_URL}" -e VU_TARGET=5 -e STEADY_DURATION=30s cpu-bound-test.js >/dev/null
  k6 run -e APP_URL="${MVC_URL}" -e VU_TARGET=5 -e STEADY_DURATION=30s io-bound-test.js >/dev/null
  k6 run -e APP_URL="${WEBFLUX_URL}" -e VU_TARGET=5 -e STEADY_DURATION=30s cpu-bound-test.js >/dev/null
  k6 run -e APP_URL="${WEBFLUX_URL}" -e VU_TARGET=5 -e STEADY_DURATION=30s io-bound-test.js >/dev/null

  echo "Smoke tests passed."
}

warmup() {
  local app_url="$1"
  echo "Warming up ${app_url} ..."
  k6 run -e APP_URL="${app_url}" -e VU_TARGET=20 -e STEADY_DURATION=2m cpu-bound-test.js >/dev/null
  k6 run -e APP_URL="${app_url}" -e VU_TARGET=20 -e STEADY_DURATION=2m io-bound-test.js >/dev/null
}

main() {
  smoke_test

  warmup "${MVC_URL}"
  warmup "${WEBFLUX_URL}"

  for repeat in $(seq 1 ${REPEATS}); do
    for vus in "${CPU_VUS[@]}"; do
      run_test "mvc" "${MVC_URL}" "cpu" "${vus}" "${repeat}"
      sleep 60
      run_test "webflux" "${WEBFLUX_URL}" "cpu" "${vus}" "${repeat}"
      sleep 60
    done

    for vus in "${IO_VUS[@]}"; do
      run_test "mvc" "${MVC_URL}" "io" "${vus}" "${repeat}"
      sleep 60
      run_test "webflux" "${WEBFLUX_URL}" "io" "${vus}" "${repeat}"
      sleep 60
    done
  done

  echo "All tests finished."
  echo "Results stored in: ${RESULTS_DIR}/${DATE_TAG}"
}

main