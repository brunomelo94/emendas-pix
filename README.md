# Emendas PIX

Scripts e notebooks para integrar dados de emendas parlamentares do tipo PIX e indicadores municipais.

## Instruções rápidas

1. Gere o arquivo `emendas_por_favorecido_partidos.csv` com a coluna de partido executando:

```bash
python src/insert_parties.py \
  --emendas data/emendas_por_favorecido.csv \
  --mapping json_data/politicos_partidos_padronizado.json \
  --out data/emendas_por_favorecido_partidos.csv
```

2. Execute o notebook `notebooks/09_unificar_dados.ipynb` para unificar os dados da pasta `data` em `data/dados_unificados.csv`.

