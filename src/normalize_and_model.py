from __future__ import annotations

import pandas as pd
from sklearn.preprocessing import StandardScaler
import statsmodels.formula.api as smf


def run_model(csv_path: str = "data/dados_com_clusters.csv") -> None:
    """Load data, normalize PIX transfers and fit mixed effects model."""
    base = pd.read_csv(csv_path)

    # Convert cluster columns to integers (0/1)
    for col in [c for c in base.columns if c.startswith("cluster_")]:
        base[col] = base[col].fillna(False).astype(int)

    # Normalize PIX per capita using z-score
    scaler = StandardScaler()
    base["emendas_pix_std"] = scaler.fit_transform(
        base[["emendas_pix_per_capita_partido_prefeito_eleito"]]
    )

    # Mixed effects model with random intercepts and slopes
    model = smf.mixedlm(
        "porcentagem_votos_validos_2024 ~ emendas_pix_std + cluster_1 + cluster_2 + cluster_3",
        base,
        groups=base["sigla_partido_prefeito_eleito"],
        re_formula="1 + emendas_pix_std",
        vc_formula={"estado": "0 + C(sigla_municipio)"},
    )
    result = model.fit()
    print(result.summary())


if __name__ == "__main__":
    run_model()
