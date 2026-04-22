import os
import json
import re
import csv

INPUT_DIR = "../../20260422_051015"
OUTPUT_FILE = "k6_results.csv"

pattern = re.compile(r"(mvc|webflux)-(cpu|io)-(\d+)-run(\d+)\.json")

rows = []

for file in os.listdir(INPUT_DIR):
    if not file.endswith(".json"):
        continue

    match = pattern.match(file)
    if not match:
        continue

    app, workload, vus, run = match.groups()
    vus = int(vus)
    run = int(run)

    path = os.path.join(INPUT_DIR, file)

    with open(path) as f:
        data = json.load(f)

    metrics = data["metrics"]

    duration = metrics["http_req_duration"]
    throughput = metrics["successful_requests"]["rate"]
    error_rate = metrics.get("http_req_failed", {}).get("value", 0)

    rows.append({
        "app": app,
        "workload": workload,
        "vus": vus,
        "run": run,
        "throughput": throughput,
        "avg": duration["avg"],
        "p95": duration["p(95)"],
        "p99": duration["p(99)"],
        "error_rate": error_rate
    })

with open(OUTPUT_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Arquivo gerado: {OUTPUT_FILE}")
