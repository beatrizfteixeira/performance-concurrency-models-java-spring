"""
Análise estatística rigorosa do experimento Spring MVC vs Spring WebFlux.

Metodologia:
- Intervalos de confiança bilaterais a 95% via distribuição t de Student
- IC de cada grupo: x̄ ± t(0.975, n-1) × s/√n
- IC da diferença (grupos independentes): diff ± t(0.975, 2n-2) × √(s²₁/n + s²₂/n)
- Coeficiente de Variação (CV) como diagnóstico de qualidade
- Teste de Shapiro-Wilk para verificar normalidade
- Classificação de qualidade da medição segundo Jain (1991):
  * CV ≤ 5%: excelente
  * CV ≤ 10%: aceitável
  * CV > 10%: precisão insuficiente

Referências:
- Jain, R. (1991). The Art of Computer Systems Performance Analysis.
- Lilja, D. J. (2000). Measuring Computer Performance.
"""

import csv
from collections import defaultdict
from math import sqrt
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import shapiro, t

INPUT_FILE = "k6_results.csv"
OUTPUT_DETAILED = "ic_detalhado.csv"
OUTPUT_COMPARISON = "ic_comparativo_mvc_vs_webflux.csv"
OUTPUT_REPORT = "RELATORIO_IC.md"

CONFIDENCE_LEVEL = 0.95
ALPHA = 1 - CONFIDENCE_LEVEL

METRICS = ["throughput", "avg", "p95", "p99"]
METRIC_LABELS = {
    "throughput": "Throughput (req/s)",
    "avg": "Latência média (ms)",
    "p95": "Latência p95 (ms)",
    "p99": "Latência p99 (ms)",
}


def t_critical(n: int, alpha: float = ALPHA) -> float:
    return float(t.ppf(1 - alpha / 2, df=n - 1))


def t_critical_diff(n1: int, n2: int, alpha: float = ALPHA) -> float:
    return float(t.ppf(1 - alpha / 2, df=n1 + n2 - 2))


def classify_cv(cv_pct: float) -> str:
    if cv_pct <= 5:
        return "Excelente"
    if cv_pct <= 10:
        return "Aceitável"
    if cv_pct <= 20:
        return "Marginal"
    return "Insuficiente"


def shapiro_test(values: list) -> tuple:
    if len(values) < 3:
        return (None, None)
    try:
        stat, p_value = shapiro(values)
        return (float(stat), float(p_value))
    except Exception:
        return (None, None)


def calcular_ic_grupo(values: np.ndarray, alpha: float = ALPHA) -> dict:
    n = len(values)
    mean = float(np.mean(values))
    median = float(np.median(values))
    std = float(np.std(values, ddof=1)) if n > 1 else 0.0
    sem = std / sqrt(n) if n > 1 else 0.0
    t_val = t_critical(n, alpha) if n > 1 else 0.0
    half_width = t_val * sem
    cv_pct = (std / mean) * 100 if mean != 0 else 0.0
    ci_pct = (half_width / mean) * 100 if mean != 0 else 0.0

    shapiro_stat, shapiro_p = shapiro_test(list(values))

    return {
        "n": n,
        "mean": mean,
        "median": median,
        "std": std,
        "sem": sem,
        "t_critical": t_val,
        "ci_half_width": half_width,
        "ci_lower": mean - half_width,
        "ci_upper": mean + half_width,
        "cv_pct": cv_pct,
        "ci_pct": ci_pct,
        "quality": classify_cv(cv_pct),
        "shapiro_stat": shapiro_stat,
        "shapiro_p": shapiro_p,
        "normal": (shapiro_p is None) or (shapiro_p >= 0.05),
    }


def calcular_ic_diferenca(values_a: np.ndarray, values_b: np.ndarray, alpha: float = ALPHA) -> dict:
    n_a = len(values_a)
    n_b = len(values_b)
    mean_a = float(np.mean(values_a))
    mean_b = float(np.mean(values_b))
    var_a = float(np.var(values_a, ddof=1)) if n_a > 1 else 0.0
    var_b = float(np.var(values_b, ddof=1)) if n_b > 1 else 0.0

    diff = mean_a - mean_b
    se_diff = sqrt(var_a / n_a + var_b / n_b)
    t_val = t_critical_diff(n_a, n_b, alpha)
    half_width = t_val * se_diff

    significant = (diff - half_width > 0) or (diff + half_width < 0)

    return {
        "diff": diff,
        "diff_pct": (diff / mean_b) * 100 if mean_b != 0 else 0.0,
        "se_diff": se_diff,
        "t_critical": t_val,
        "ci_half_width": half_width,
        "ci_lower": diff - half_width,
        "ci_upper": diff + half_width,
        "significant_p005": significant,
    }


def carregar_dados(input_file: str) -> pd.DataFrame:
    df = pd.read_csv(input_file)
    df["app"] = df["app"].str.lower()
    df["workload"] = df["workload"].str.lower()
    return df


def gerar_ic_detalhado(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    grouped = df.groupby(["app", "workload", "vus"])

    for (app, workload, vus), group in grouped:
        for metric in METRICS:
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
                "ci_pct": stats["ci_pct"],
                "cv_pct": stats["cv_pct"],
                "quality": stats["quality"],
                "shapiro_p": stats["shapiro_p"],
                "normal_distribution": stats["normal"],
            })

    return pd.DataFrame(rows)


def gerar_ic_comparativo(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    workloads = sorted(df["workload"].unique())

    for workload in workloads:
        wf_df = df[df["workload"] == workload]
        vus_levels = sorted(wf_df["vus"].unique())

        for vus in vus_levels:
            mvc_group = wf_df[(wf_df["app"] == "mvc") & (wf_df["vus"] == vus)]
            wfx_group = wf_df[(wf_df["app"] == "webflux") & (wf_df["vus"] == vus)]

            if mvc_group.empty or wfx_group.empty:
                continue

            for metric in METRICS:
                mvc_values = mvc_group[metric].to_numpy()
                wfx_values = wfx_group[metric].to_numpy()

                mvc_stats = calcular_ic_grupo(mvc_values)
                wfx_stats = calcular_ic_grupo(wfx_values)
                diff_stats = calcular_ic_diferenca(mvc_values, wfx_values)

                rows.append({
                    "workload": workload,
                    "vus": vus,
                    "metric": metric,
                    "mvc_mean": mvc_stats["mean"],
                    "mvc_ci_lower": mvc_stats["ci_lower"],
                    "mvc_ci_upper": mvc_stats["ci_upper"],
                    "mvc_cv_pct": mvc_stats["cv_pct"],
                    "wf_mean": wfx_stats["mean"],
                    "wf_ci_lower": wfx_stats["ci_lower"],
                    "wf_ci_upper": wfx_stats["ci_upper"],
                    "wf_cv_pct": wfx_stats["cv_pct"],
                    "diff_mvc_minus_wf": diff_stats["diff"],
                    "diff_pct": diff_stats["diff_pct"],
                    "diff_ci_lower": diff_stats["ci_lower"],
                    "diff_ci_upper": diff_stats["ci_upper"],
                    "significant_p005": diff_stats["significant_p005"],
                })

    return pd.DataFrame(rows)


def fmt(value: float, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_relatorio_markdown(df_detail: pd.DataFrame, df_comp: pd.DataFrame, output_file: str) -> None:
    lines = []
    lines.append("# Análise Estatística — Spring MVC vs Spring WebFlux\n")
    lines.append("## 1. Metodologia\n")
    lines.append(
        "- **Intervalo de Confiança**: bilateral a 95% via distribuição **t de Student**.\n"
        "- IC de cada grupo: `x̄ ± t(0,975; n−1) × s/√n`. Para `n=3` → `t = 4,303`.\n"
        "- IC da diferença (grupos independentes): `(x̄₁ − x̄₂) ± t(0,975; n₁+n₂−2) × √(s²₁/n₁ + s²₂/n₂)`.\n"
        "  Para `n=3` em cada grupo → `t = 2,776`.\n"
        "- **Coeficiente de Variação (CV)**: `s/x̄ × 100`. Classificação por Jain (1991):\n"
        "  - CV ≤ 5%: Excelente\n"
        "  - 5% < CV ≤ 10%: Aceitável\n"
        "  - 10% < CV ≤ 20%: Marginal\n"
        "  - CV > 20%: Insuficiente (precisa de mais repetições)\n"
        "- **Teste de Shapiro-Wilk**: verifica se a distribuição é normal (`p ≥ 0,05` → não rejeita normalidade).\n"
        "- **Significância da diferença**: o IC da diferença não inclui zero → diferença significativa a 5%.\n"
    )

    lines.append("\n## 2. Limitação Conhecida\n")
    lines.append(
        "Os percentis (p95, p99) foram calculados pelo k6 sobre **toda a duração do teste**, "
        "incluindo as fases de ramp-up (30s) e ramp-down (30s). Isso pode inflar a variabilidade "
        "dos percentis de cauda entre repetições. As métricas `throughput` e `avg` são mais "
        "robustas a esse efeito porque dependem do volume total de dados.\n"
    )

    lines.append("\n## 3. Resumo de Qualidade das Medições\n")
    quality_summary = df_detail.groupby(["metric", "quality"]).size().unstack(fill_value=0)
    quality_summary = quality_summary.reindex(columns=["Excelente", "Aceitável", "Marginal", "Insuficiente"], fill_value=0)
    lines.append("| Métrica | Excelente (CV≤5%) | Aceitável (≤10%) | Marginal (≤20%) | Insuficiente (>20%) |")
    lines.append("|---|---:|---:|---:|---:|")
    for metric in METRICS:
        if metric in quality_summary.index:
            row = quality_summary.loc[metric]
            lines.append(f"| {METRIC_LABELS[metric]} | {row['Excelente']} | {row['Aceitável']} | {row['Marginal']} | {row['Insuficiente']} |")

    lines.append("\n## 4. Resumo de Normalidade (Shapiro-Wilk)\n")
    normal_count = df_detail.groupby("metric")["normal_distribution"].agg(["sum", "count"])
    lines.append("| Métrica | Distribuições normais | Total | % normais |")
    lines.append("|---|---:|---:|---:|")
    for metric in METRICS:
        if metric in normal_count.index:
            row = normal_count.loc[metric]
            pct = (row["sum"] / row["count"]) * 100
            lines.append(f"| {METRIC_LABELS[metric]} | {int(row['sum'])} | {int(row['count'])} | {pct:.0f}% |")

    lines.append("\n## 5. Intervalos de Confiança por Configuração\n")
    for workload in sorted(df_detail["workload"].unique()):
        lines.append(f"\n### 5.{['cpu', 'io'].index(workload) + 1} Workload `{workload}`-bound\n")
        for metric in METRICS:
            lines.append(f"\n#### {METRIC_LABELS[metric]}\n")
            lines.append("| VUs | App | Média | IC 95% | CV % | Qualidade | Normal? |")
            lines.append("|---|---|---:|---|---:|---|:---:|")
            sub = df_detail[(df_detail["workload"] == workload) & (df_detail["metric"] == metric)]
            sub = sub.sort_values(["vus", "app"])
            for _, row in sub.iterrows():
                ic_str = f"[{fmt(row['ci_lower'])} ; {fmt(row['ci_upper'])}]"
                normal_str = "✓" if row["normal_distribution"] else "✗"
                lines.append(
                    f"| {int(row['vus'])} | {row['app']} | {fmt(row['mean'])} | {ic_str} | "
                    f"{fmt(row['cv_pct'])} | {row['quality']} | {normal_str} |"
                )

    lines.append("\n## 6. Comparação MVC vs WebFlux\n")
    lines.append(
        "Diferença = MVC − WebFlux. **Sig.** indica que o IC da diferença exclui zero (p < 0,05). "
        "Para throughput, MVC > WebFlux significa diferença positiva. "
        "Para latências, MVC > WebFlux (positivo) indica que MVC é mais lento.\n"
    )
    for workload in sorted(df_comp["workload"].unique()):
        lines.append(f"\n### 6.{['cpu', 'io'].index(workload) + 1} Workload `{workload}`-bound\n")
        for metric in METRICS:
            lines.append(f"\n#### {METRIC_LABELS[metric]}\n")
            lines.append("| VUs | MVC (média ± IC) | WebFlux (média ± IC) | Δ (MVC−WF) | IC da Δ | Sig.? |")
            lines.append("|---|---|---|---:|---|:---:|")
            sub = df_comp[(df_comp["workload"] == workload) & (df_comp["metric"] == metric)]
            sub = sub.sort_values("vus")
            for _, row in sub.iterrows():
                mvc_hw = (row["mvc_ci_upper"] - row["mvc_ci_lower"]) / 2
                wf_hw = (row["wf_ci_upper"] - row["wf_ci_lower"]) / 2
                diff_ic = f"[{fmt(row['diff_ci_lower'])} ; {fmt(row['diff_ci_upper'])}]"
                sig = "✓" if row["significant_p005"] else "✗"
                lines.append(
                    f"| {int(row['vus'])} | {fmt(row['mvc_mean'])} ± {fmt(mvc_hw)} | "
                    f"{fmt(row['wf_mean'])} ± {fmt(wf_hw)} | {fmt(row['diff_mvc_minus_wf'])} | "
                    f"{diff_ic} | {sig} |"
                )

    lines.append("\n## 7. Conclusões\n")
    insufic = df_detail[df_detail["quality"] == "Insuficiente"]
    if not insufic.empty:
        lines.append(
            f"\n- **{len(insufic)} configuração(ões)** apresentaram CV > 20% (precisão insuficiente). "
            "Recomenda-se aumentar o número de repetições para essas configurações.\n"
        )
        lines.append("\nConfigurações com precisão insuficiente:\n")
        lines.append("| App | Workload | VUs | Métrica | CV % |")
        lines.append("|---|---|---:|---|---:|")
        for _, row in insufic.iterrows():
            lines.append(f"| {row['app']} | {row['workload']} | {int(row['vus'])} | {row['metric']} | {fmt(row['cv_pct'])} |")
    else:
        lines.append("- Todas as configurações apresentaram precisão Marginal ou superior (CV ≤ 20%).\n")

    sig_count = df_comp[df_comp["significant_p005"]].shape[0]
    total = len(df_comp)
    lines.append(
        f"\n- **{sig_count}/{total}** comparações entre MVC e WebFlux apresentaram diferença "
        f"estatisticamente significativa (IC da diferença exclui zero, p < 0,05).\n"
    )

    Path(output_file).write_text("\n".join(lines), encoding="utf-8")


def main():
    print("Carregando dados...")
    df = carregar_dados(INPUT_FILE)
    print(f"  → {len(df)} linhas carregadas.")

    print("Calculando ICs por configuração...")
    df_detail = gerar_ic_detalhado(df)
    df_detail.to_csv(OUTPUT_DETAILED, index=False)
    print(f"  → {OUTPUT_DETAILED}")

    print("Calculando ICs comparativos MVC vs WebFlux...")
    df_comp = gerar_ic_comparativo(df)
    df_comp.to_csv(OUTPUT_COMPARISON, index=False)
    print(f"  → {OUTPUT_COMPARISON}")

    print("Gerando relatório markdown...")
    gerar_relatorio_markdown(df_detail, df_comp, OUTPUT_REPORT)
    print(f"  → {OUTPUT_REPORT}")

    print("\n=== Resumo ===")
    quality_counts = df_detail["quality"].value_counts()
    for quality in ["Excelente", "Aceitável", "Marginal", "Insuficiente"]:
        count = quality_counts.get(quality, 0)
        print(f"  {quality}: {count} configurações")

    sig = df_comp["significant_p005"].sum()
    print(f"\n  Comparações com diferença significativa (p<0,05): {sig}/{len(df_comp)}")


if __name__ == "__main__":
    main()
