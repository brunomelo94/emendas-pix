import pandas as pd
import re
from unidecode import unidecode


def _normalize_municipio(nome: str) -> str:
    """Normalize municipality names to 'MUNICIPIO - UF' without accents."""
    if pd.isna(nome):
        return None
    nome = unidecode(str(nome)).upper().strip()
    # attempt to extract UF within parentheses or after dash
    m = re.search(r"\((\w{2})\)$", nome)
    uf = None
    if m:
        uf = m.group(1)
        base = nome[:m.start()].strip()
    else:
        # look for ' - UF' pattern
        m = re.search(r"\s-\s([A-Z]{2})$", nome)
        if m:
            uf = m.group(1)
            base = nome[:m.start()].strip()
        else:
            base = nome
    return f"{base} - {uf}" if uf else base


def load_emendas(path: str) -> pd.DataFrame:
    """Load PIX amendments data and clean columns."""
    df = pd.read_csv(path, encoding="utf-8-sig")
    # drop unnamed empty columns
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df["municipio"] = (df["Nome Ente"] + " - " + df["UF"]).apply(_normalize_municipio)
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    df = df.dropna(subset=["municipio", "Valor"])
    df = df.reset_index(drop=True)
    return df


def load_resultados(path: str) -> pd.DataFrame:
    """Load election results."""
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["municipio"] = (df["NM_MUNICIPIO"] + " - " + df["SG_UF"]).apply(_normalize_municipio)
    df = df.drop_duplicates(subset=["municipio", "NM_CANDIDATO"])
    df = df.reset_index(drop=True)
    return df


def load_ibge_indicators(densidade_path: str, escolar_path: str, idhm_path: str, pib_path: str) -> pd.DataFrame:
    """Load socio-economic indicators from IBGE related datasets and merge them."""
    dens = pd.read_csv(densidade_path)
    dens = dens.rename(columns={"name_muni_x": "municipio_raw", "population_2022": "populacao_2022"})
    dens["municipio"] = dens["municipio_raw"].apply(_normalize_municipio)
    dens = dens.drop(columns=["municipio_raw", "name_muni_y"])

    escolar = pd.read_csv(escolar_path)
    escolar["municipio"] = escolar["Territorialidades"].apply(_normalize_municipio)
    escolar = escolar.drop(columns=["Territorialidades"])

    idhm = pd.read_csv(idhm_path)
    idhm["municipio"] = idhm["Territorialidades"].apply(_normalize_municipio)
    idhm = idhm.drop(columns=["Territorialidades"])

    pib = pd.read_csv(pib_path)
    pib["municipio"] = pib["name_muni"].apply(_normalize_municipio)
    pib = pib.drop(columns=["name_muni"])

    # Merge all on municipio
    df = dens.merge(escolar, on="municipio", how="left")
    df = df.merge(idhm, on="municipio", how="left")
    df = df.merge(pib, on="municipio", how="left")

    # handle missing numeric values by filling with median
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        if df[col].isna().any():
            df[col].fillna(df[col].median(), inplace=True)
    df = df.reset_index(drop=True)
    return df


def integrate_dados(emendas: pd.DataFrame, resultados: pd.DataFrame, ibge: pd.DataFrame) -> pd.DataFrame:
    """Integrate PIX amendments, election results and IBGE indicators."""
    df = resultados.merge(ibge, on="municipio", how="left")
    emendas_agg = (
        emendas.groupby("municipio", as_index=False)["Valor"].sum()
        .rename(columns={"Valor": "valor_pix_total"})
    )
    df = df.merge(emendas_agg, on="municipio", how="left")
    df["valor_pix_total"].fillna(0, inplace=True)
    return df


if __name__ == "__main__":
    emendas = load_emendas("data/emendas.csv")
    resultados = load_resultados("data/resultados_eleicoes.csv")
    ibge = load_ibge_indicators(
        "data/densidade.csv",
        "data/escolarizacao.csv",
        "data/idhm.csv",
        "data/pib_per_capita.csv",
    )
    final = integrate_dados(emendas, resultados, ibge)
    final.to_csv("data/dados_integrados.csv", index=False)
    print("Arquivo salvo em data/dados_integrados.csv")
