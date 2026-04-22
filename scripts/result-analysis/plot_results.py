import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("aggregated_results.csv")

def plot_metric(metric, workload):
    subset = df[(df["metric"] == metric) & (df["workload"] == workload)]

    plt.figure(figsize=(10, 6))

    for app in subset["app"].unique():
        data = subset[subset["app"] == app].sort_values("vus")

        plt.errorbar(
            data["vus"],
            data["mean"],
            yerr=data["ci"],
            label=app.upper(),
            capsize=3,
            marker='o'
        )

    plt.xlabel("VUs (Usuários Virtuais)")
    plt.ylabel(metric.upper() if metric == "throughput" else f"Latência {metric.upper()} (ms)")
    plt.title(f"{metric.upper()} vs VUs - Workload {workload.upper()}-bound")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    filename = f"{metric}_{workload}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Gráfico salvo: {filename}")

plot_metric("throughput", "cpu")
plot_metric("p95", "cpu")

plot_metric("throughput", "io")
plot_metric("p95", "io")
