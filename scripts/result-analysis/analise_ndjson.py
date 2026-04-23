"""
Análise de NDJSON do k6 com filtragem de ramp-up/ramp-down.

Este script processa os arquivos NDJSON raw gerados pelo k6 (--out json=)
e recalcula percentis e intervalos de confiança considerando APENAS
a fase de steady-state (excluindo ramp-up de 30s e ramp-down de 30s).

Metodologia estatística (idêntica a analise_estatistica.py):
- IC bilateral 95% via distribuição t de Student
- IC de cada grupo: x̄ ± t(0,975; n-1) × s/√n
- Coeficiente de Variação como diagnóstico de qualidade
- Classificação por Jain (1991): Excelente / Aceitável / Marginal / Insuficiente
"""

import json
import re
from datetime import datetime, timezone
from math import sqrt
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t

INPUT_DIR = "rerun_results"
OUTPUT_FILE = "k6_results_filtered.csv"
OUTPUT_IC = "ic_filtered.csv"

RAMP_UP_SECONDS = 30
RAMP_DOWN_SECONDS = 30

CONFIDENCE_LEVEL = 0.95
ALPHA = 1 - CONFIDENCE_LEVEL

PATTERN = re.compile(r"(mvc|webflux)-(cpu|io)-(\d+)-run(\d+)-raw\.json")


def parse_iso_timestamp(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def carregar_ndjson(filepath: Path) -> tuple:
    durations = []
    timestamps = []

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            if obj.get("type") != "Point":
                continue

            metric = obj.get("metric")
            if metric != "http_req_duration":
                continue

            data = obj.get("data", {})
            tags = data.get("tags", {})

            if tags.get("expected_response") != "true":
                continue

            value = data.get("value")
            time_str = data.get("time")

            if value is None or time_str is None:
                continue

            durations.append(float(value))
            timestamps.append(parse_iso_timestamp(time_str))

    return durations, timestamps


def filtrar_steady_state(durations: list, timestamps: list,
                         ramp_up_s: int = RAMP_UP_SECONDS,
                         ramp_down_s: int = RAMP_DOWN_SECONDS) -> list:
    if not timestamps:
        return []

    test_start = min(timestamps)
    test_end = max(timestamps)
    steady_start = test_start.timestamp() + ramp_up_s
    steady_end = test_end.timestamp() - ramp_down_s

    filtered = [
        d for d, ts in zip(durations, timestamps)
        if steady_start <= ts.timestamp() <= steady_end
    ]

    return filtered


def calcular_metricas(durations: list, duration_seconds: float) -> dict:
    if not durations:
        return {
            "throughput": 0.0,
            "avg": 0.0,
            "p95": 0.0,
            "p99": 0.0,
            "count": 0,
        }

    arr = np.array(durations)
    return {
        "throughput": len(arr) / duration_seconds if duration_seconds > 0 else 0.0,
        "avg": float(np.mean(arr)),
        "p95": float(np.percentile(arr, 95)),
        "p99": float(np.percentile(arr, 99)),
        "count": len(arr),
    }


def t_critical(n: int, alpha: float = ALPHA) -> float:
    return float(t.ppf(1 - alpha / 2, df=n - 1))


def classify_cv(cv_pct: float) -> str:
    if cv_pct <= 5:
        return "Excelente"
    if cv_pct <= 10:
        return "Aceitável"
    if cv_pct <= 20:
        return "Marginal"
    return "Insuficiente"


def calcular_ic_grupo(values: np.ndarray, alpha: float = ALPHA) -> dict:
    n = len(values)
    mean = float(np.mean(values))
    median = float(np.median(values))
    std = float(np.std(values, ddof=1)) if n > 1 else 0.0
    sem = std / sqrt(n) if n > 1 else 0.0
    t_val = t_critical(n, alpha) if n > 1 else 0.0
    half_width = t_val * sem
    cv_pct = (std / mean) * 100 if mean != 0 else 0.0

    return {
        "n": n,
        "mean": mean,
        "median": median,
        "std": std,
        "ci_lower": mean - half_width,
        "ci_upper": mean + half_width,
        "ci_half_width": half_width,
        "cv_pct": cv_pct,
        "quality": classify_cv(cv_pct),
    }


def processar_arquivos(input_dir: str) -> pd.DataFrame:
    rows = []
    input_path = Path(input_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"Diretório não encontrado: {input_dir}")

    files = sorted(input_path.glob("*-raw.json"))
    if not files:
        raise FileNotFoundError(f"Nenhum arquivo *-raw.json em {input_dir}")

    print(f"Encontrados {len(files)} arquivos NDJSON para processar.")

    for filepath in files:
        match = PATTERN.match(filepath.name)
        if not match:
            print(f"  Ignorado (não bate com o padrão): {filepath.name}")
            continue

        app, workload, vus, run = match.groups()
        print(f"  Processando {filepath.name}...")

        durations, timestamps = carregar_ndjson(filepath)

        if not durations:
            print(f"    Aviso: sem dados de http_req_duration em {filepath.name}")
            continue

        filtered = filtrar_steady_state(durations, timestamps)
        if not filtered:
            print(f"    Aviso: sem dados após filtragem em {filepath.name}")
            continue

        steady_seconds = (max(timestamps) - min(timestamps)).total_seconds() - RAMP_UP_SECONDS - RAMP_DOWN_SECONDS
        metricas = calcular_metricas(filtered, steady_seconds)

        rows.append({
            "app": app,
            "workload": workload,
            "vus": int(vus),
            "run": int(run),
            "n_filtered": metricas["count"],
            "n_total": len(durations),
            "throughput": metricas["throughput"],
            "avg": metricas["avg"],
            "p95": metricas["p95"],
            "p99": metricas["p99"],
        })

    return pd.DataFrame(rows)


def calcular_ics(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    metrics = ["throughput", "avg", "p95", "p99"]

    for (app, workload, vus), group in df.groupby(["app", "workload", "vus"]):
        for metric in metrics:
            values = group[metric].to_numpy()
            stats = calcular_ic_grupo(values)
            rows.append({
                "app": app,
                "workload": workload,
                "vus": vus,
                "metric": metric,
                "n": stats["n"],
                "mean": stats["mean"],
                "median": stats["median"],
                "std": stats["std"],
                "ci_lower": stats["ci_lower"],
                "ci_upper": stats["ci_upper"],
                "ci_half_width": stats["ci_half_width"],
                "cv_pct": stats["cv_pct"],
                "quality": stats["quality"],
            })

    return pd.DataFrame(rows)


def main():
    print("=" * 60)
    print("Análise NDJSON com filtragem de ramp-up/ramp-down")
    print(f"Ramp-up: {RAMP_UP_SECONDS}s | Ramp-down: {RAMP_DOWN_SECONDS}s")
    print("=" * 60)

    df_raw = processar_arquivos(INPUT_DIR)
    df_raw.to_csv(OUTPUT_FILE, index=False)
    print(f"\nResultados por execução: {OUTPUT_FILE}")

    df_ic = calcular_ics(df_raw)
    df_ic.to_csv(OUTPUT_IC, index=False)
    print(f"Intervalos de confiança: {OUTPUT_IC}")

    print("\n=== Comparação com dados originais (com ramp-up) ===")
    for (app, workload, vus), group in df_raw.groupby(["app", "workload", "vus"]):
        print(f"\n  {app}-{workload}-{vus}:")
        for metric in ["p95", "p99"]:
            stats = calcular_ic_grupo(group[metric].to_numpy())
            print(f"    {metric}: média={stats['mean']:.2f}ms  "
                  f"IC=[{stats['ci_lower']:.2f}; {stats['ci_upper']:.2f}]  "
                  f"CV={stats['cv_pct']:.2f}%  ({stats['quality']})")


if __name__ == "__main__":
    main()
