from __future__ import annotations

"""Check if PIX transfers influence vote percentage using a mixed effects model."""

import argparse
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf
from sklearn.preprocessing import StandardScaler


def check_effect(csv_path: str | Path = "data/dados_com_clusters.csv") -> float:
    """Return p-value for the effect of PIX per capita on vote percentage."""
    df = pd.read_csv(csv_path)

    # Ensure cluster columns are integer flags
    for col in [c for c in df.columns if c.startswith("cluster_")]:
        df[col] = df[col].fillna(False).astype(int)

    # Standardize PIX per capita for stability in the model
    scaler = StandardScaler()
    df["pix_std"] = scaler.fit_transform(
        df[["emendas_pix_per_capita_partido_prefeito_eleito"]]
    )

    # Mixed effects model with party as grouping factor
    model = smf.mixedlm(
        "porcentagem_votos_validos_2024 ~ pix_std + cluster_0 + cluster_1 + cluster_2 + cluster_3",
        df,
        groups=df["sigla_partido_prefeito_eleito"],
        re_formula="1 + pix_std",
    )
    result = model.fit()

    p_val = float(result.pvalues.get("pix_std", 1.0))
    coef = float(result.params.get("pix_std", float("nan")))

    print(result.summary())
    print(f"\nCoefficient: {coef:.4f}, p-value: {p_val:.4f}")

    if p_val < 0.05:
        print("The effect of emendas_pix_per_capita_partido_prefeito_eleito is statistically significant.")
    else:
        print("No statistically significant effect found for emendas_pix_per_capita_partido_prefeito_eleito.")

    return p_val


def main() -> None:
    parser = argparse.ArgumentParser(description="Check significance of PIX transfers in vote percentage")
    parser.add_argument(
        "--csv",
        default="data/dados_com_clusters.csv",
        help="CSV file with election data and PIX transfers",
    )
    args = parser.parse_args()
    check_effect(args.csv)


if __name__ == "__main__":
    main()
