from __future__ import annotations

import logging

try:
    from .party_service import add_parties_to_csv
except ImportError:  # pragma: no cover - allows running as script
    from party_service import add_parties_to_csv


def main(csv_path: str) -> None:
    add_parties_to_csv(csv_path)


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Add SG_PARTIDO column to emendas CSV")
    parser.add_argument("csv_path", help="Path to emendas_por_favorecido.csv")

    args = parser.parse_args()
    main(args.csv_path)