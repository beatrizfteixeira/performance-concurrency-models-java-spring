"""
Filtra CSVs brutos do k6 para conter apenas as requests do steady state.

De cada request, mantém apenas a linha de http_req_duration (que é a métrica
de latência total). Gera um CSV limpo com uma linha por request.

Uso:
    python3 filtrar_csv_steady.py <pasta_entrada> [<pasta_saida>]

Exemplo:
    python3 filtrar_csv_steady.py ~/Documentos/resultados-cpu-bound-26-04-1/
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path


COLUNAS_SAIDA: list[str] = [
    "timestamp",
    "duration_ms",
    "status",
    "scenario",
    "method",
    "url",
]


def filtrar_arquivo(arquivo_entrada: Path, arquivo_saida: Path) -> int:
    """Filtra um CSV raw do k6 mantendo apenas http_req_duration do steady.

    Retorna o número de linhas escritas no CSV de saída.
    """
    final_linhas_escritas: int = 0

    with arquivo_entrada.open("r", encoding="utf-8", newline="") as f_in:
        final_reader = csv.DictReader(f_in)

        with arquivo_saida.open("w", encoding="utf-8", newline="") as f_out:
            final_writer = csv.DictWriter(f_out, fieldnames=COLUNAS_SAIDA)
            final_writer.writeheader()

            for linha in final_reader:
                if linha.get("metric_name") != "http_req_duration":
                    continue
                if linha.get("scenario") != "steady":
                    continue

                final_writer.writerow(
                    {
                        "timestamp": linha.get("timestamp", ""),
                        "duration_ms": linha.get("metric_value", ""),
                        "status": linha.get("status", ""),
                        "scenario": linha.get("scenario", ""),
                        "method": linha.get("method", ""),
                        "url": linha.get("url", ""),
                    }
                )
                final_linhas_escritas += 1

    return final_linhas_escritas


def processar_pasta(pasta_entrada: Path, pasta_saida: Path) -> None:
    """Processa todos os arquivos *-raw.csv de uma pasta."""
    pasta_saida.mkdir(parents=True, exist_ok=True)

    final_arquivos_raw: list[Path] = sorted(pasta_entrada.glob("*-raw.csv"))

    if not final_arquivos_raw:
        print(f"Nenhum arquivo *-raw.csv encontrado em: {pasta_entrada}")
        return

    print(f"Processando {len(final_arquivos_raw)} arquivo(s)...\n")

    for arquivo in final_arquivos_raw:
        final_nome_saida: str = arquivo.stem.replace("-raw", "-steady") + ".csv"
        final_arquivo_saida: Path = pasta_saida / final_nome_saida

        final_n_linhas: int = filtrar_arquivo(arquivo, final_arquivo_saida)

        print(
            f"  {arquivo.name}"
            f"\n    --> {final_arquivo_saida.name} ({final_n_linhas} requests steady)"
        )


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    final_pasta_entrada: Path = Path(sys.argv[1]).expanduser().resolve()

    if len(sys.argv) >= 3:
        final_pasta_saida: Path = Path(sys.argv[2]).expanduser().resolve()
    else:
        final_pasta_saida = final_pasta_entrada / "steady"

    if not final_pasta_entrada.is_dir():
        print(f"Erro: pasta de entrada nao existe: {final_pasta_entrada}")
        sys.exit(1)

    print(f"Pasta entrada: {final_pasta_entrada}")
    print(f"Pasta saida:   {final_pasta_saida}\n")

    processar_pasta(final_pasta_entrada, final_pasta_saida)

    print("\nConcluido.")


if __name__ == "__main__":
    main()
