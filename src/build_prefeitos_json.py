from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def csv_to_prefeito_json(input_csv: str | Path, output_json: str | Path) -> int:
    """Create JSON mapping municipality to elected mayor.

    Parameters
    ----------
    input_csv : str | Path
        CSV file with columns ``municipio`` and ``prefeito_eleito_2024``.
    output_json : str | Path
        Path to write JSON output.

    Returns
    -------
    int
        Number of municipalities written to ``output_json``.
    """
    df = pd.read_csv(input_csv, encoding="utf-8-sig")
    mapping = (
        df[["municipio", "prefeito_eleito_2024"]]
        .drop_duplicates(subset="municipio")
        .set_index("municipio")
        ["prefeito_eleito_2024"]
        .dropna()
        .astype(str)
        .to_dict()
    )
    with Path(output_json).open("w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    return len(mapping)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate JSON with elected mayors by municipality"
    )
    parser.add_argument(
        "--csv",
        default="data/dados_unificados_prefeitos_200k.csv",
        help="Input CSV path",
    )
    parser.add_argument(
        "--out",
        default="json_data/prefeitos_2024.json",
        help="Output JSON file path",
    )
    args = parser.parse_args()
    count = csv_to_prefeito_json(args.csv, args.out)
    print(f"JSON generated: {args.out} ({count} municipalities)")


if __name__ == "__main__":
    main()
