import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv("k6_results.csv")

grouped = df.groupby(["app", "workload", "vus"])

results = []

for name, group in grouped:
    n = len(group)

    for metric in ["throughput", "avg", "p95", "p99"]:
        mean = group[metric].mean()
        std = group[metric].std(ddof=1)

        # t-student para n=3 → ~4.303
        t = stats.t.ppf(0.975, df=n-1)

        ci = t * (std / np.sqrt(n))

        results.append({
            "app": name[0],
            "workload": name[1],
            "vus": name[2],
            "metric": metric,
            "mean": mean,
            "ci": ci
        })

agg_df = pd.DataFrame(results)
agg_df.to_csv("aggregated_results.csv", index=False)

print("Arquivo gerado: aggregated_results.csv")
