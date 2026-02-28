# TCC — Emendas PIX e Desempenho Eleitoral Municipal (2024)

**Aluno:** Bruno Caetano Oliveira de Melo
**Orientadora:** Adâmara Santos Gonçalves Felício
**Curso:** MBA em Data Science e Analytics — USP/Esalq

---

## Resumo do Projeto

Avalia se o volume per capita de Emendas PIX alocado por deputados federais está associado a maior probabilidade de reeleição ou melhor desempenho eleitoral dos prefeitos aliados nas eleições municipais de 2024.

**Resultado principal:** Associação positiva e altamente significativa (p < 0,001) em todos os modelos estimados.

---

## Estrutura de Notebooks

Execute na ordem:

| Notebook | Descrição |
|---|---|
| `01_unificar_dados.ipynb` | Unificação dos dados brutos (CGU, TSE, IBGE) |
| `02_exploratory_analysis.ipynb` | Análise exploratória e distribuições |
| `03_clustering.ipynb` | Clusterização k-means dos municípios (k=3) |
| `04_analise_clusters_emendas.ipynb` | Análise de emendas por cluster socioeconômico |
| `05_resultados_preliminares.ipynb` | Resultados preliminares (entregues ao orientador) |
| **`06_modeling_final.ipynb`** | **Modelagem final — GEE + Multinível Linear** |

Notebooks antigos: `notebooks/_arquivo/`

---

## Configuração do Ambiente

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar (Windows)
.venv\Scripts\activate

# Instalar dependências
pip install pandas numpy matplotlib seaborn statsmodels scikit-learn scipy jupyter nbconvert
```

---

## Pipeline de Dados

### 1. Preparar dados de emendas com partidos

```bash
python src/insert_parties.py \
  --emendas data/emendas_por_favorecido.csv \
  --mapping json_data/politicos_partidos_padronizado.json \
  --out data/emendas_por_favorecido_partidos.csv
```

### 2. Unificar dados

Execute `01_unificar_dados.ipynb` → gera `data/dados_unificados_prefeitos_200k.csv`

### 3. Clusterização

Execute `03_clustering.ipynb` → gera `data/dados_com_clusters.csv`

### 4. Modelagem final

Execute `06_modeling_final.ipynb` → gera figuras em `data/fig_*.png`

---

## Dados Necessários (pasta `data/`)

| Arquivo | Descrição |
|---|---|
| `dados_com_clusters.csv` | Base principal com dummies de cluster (5.208 municípios) |
| `emendas_por_favorecido_partidos.csv` | Emendas PIX com partidos dos deputados |
| `resultados_eleicoes.csv` | Resultados TSE 2024 |

---

## Resultados Principais

| Modelo | VD | N | log_emenda | p-valor |
|--------|-----|---|-----------|---------|
| A1 (LMM) | % votos | 4.935 | β = 0.019 | < 0,001 *** |
| A2 (LMM+clusters) | % votos | 4.935 | β = 0.016 | < 0,001 *** |
| B0 (GEE) | Maioria (bin.) | 5.197 | OR = 1.68 | < 0,001 *** |
| B1 (GEE+clusters) | Maioria (bin.) | 5.197 | OR = 1.57 | < 0,001 *** |

**Efeito deterrence (Q4 vs Q1):** +11,9 pp na taxa de vitória por maioria absoluta; +5,6 pp em candidaturas únicas.
