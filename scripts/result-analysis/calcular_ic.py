import pandas as pd
import numpy as np
from scipy.stats import t

df = pd.read_csv("k6_results.csv")

grouped = df.groupby(["app", "workload", "vus"])

results = []

for (app, workload, vus), group in grouped:
    n = len(group)
    t_value = t.ppf(0.975, df=n-1)

    for metric in ["throughput", "avg", "p95", "p99"]:
        mean = group[metric].mean()
        std = group[metric].std(ddof=1)

        ci = t_value * (std / np.sqrt(n))

        results.append({
            "app": app,
            "workload": workload,
            "vus": vus,
            "metric": metric,
            "mean": mean,
            "ci_lower": mean - ci,
            "ci_upper": mean + ci,
            "ci_half_width": ci,
            "ci_percent": (ci / mean) * 100 if mean != 0 else 0
        })

result_df = pd.DataFrame(results)
result_df.to_csv("ci_results.csv", index=False)

print("Arquivo gerado: ci_results.csv")
