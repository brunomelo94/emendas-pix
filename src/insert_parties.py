from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd


logger = logging.getLogger(__name__)


def add_parties(emendas_path: str | Path,
                mapping_path: str | Path,
                out_path: str | Path) -> int:
    """Add party acronym to emendas CSV.

    Parameters
    ----------
    emendas_path : str | Path
        Input CSV path (emendas_por_favorecido.csv).
    mapping_path : str | Path
        JSON file with mapping from author name to party.
    out_path : str | Path
        Output CSV path.
    Returns
    -------
    int
        Number of rows written to ``out_path``.
    """
    emendas_df = pd.read_csv(emendas_path, encoding="utf-8-sig")
    with Path(mapping_path).open("r", encoding="utf-8") as f:
        mapping: dict[str, str] = json.load(f)

    emendas_df["siglaPartido"] = emendas_df["Nome do Autor da Emenda"].map(mapping).fillna("UNKNOWN")
    emendas_df.to_csv(out_path, index=False, encoding="utf-8-sig")
    return len(emendas_df)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Insere coluna de partido no CSV de emendas")
    parser.add_argument(
        "--emendas",
        default="data/emendas_por_favorecido.csv",
        help="CSV de entrada",
    )
    parser.add_argument(
        "--mapping",
        default="json_data/politicos_partidos_padronizado.json",
        help="JSON com mapeamento de nomes para partidos",
    )
    parser.add_argument(
        "--out",
        default="data/emendas_por_favorecido_partidos.csv",
        help="CSV de saída com partidos",
    )

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    rows = add_parties(args.emendas, args.mapping, args.out)
    logger.info("Arquivo gerado: %s (%d linhas)", args.out, rows)


if __name__ == "__main__":
    main()
