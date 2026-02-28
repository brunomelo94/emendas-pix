# Revisão Crítica da Metodologia — TCC Emendas PIX

**Aluno:** Bruno Caetano Oliveira de Melo
**Orientadora:** Adâmara Santos Gonçalves Felício
**Data:** Fevereiro/2026

> Este documento apresenta uma análise crítica e aprofundada de cada decisão metodológica do TCC, com justificativas teóricas, limitações conhecidas e respostas defensáveis para uma banca de avaliação.

---

## Sumário

1. [Escopo da amostra (municípios 2k–200k)](#1-escopo-da-amostra)
2. [Variável dependente: escolha e construção](#2-variável-dependente)
3. [Variável explicativa principal: log(1+PIX)](#3-transformação-logarítmica-da-variável-explicativa)
4. [Winsorização (1% cada cauda)](#4-winsorização)
5. [Clusterização K-Means como controles](#5-clusterização-k-means-como-controles)
6. [Modelo A — Multinível Linear (LMM)](#6-modelo-a--multinível-linear)
   - 6a. Justificativa para LMM
   - 6b. Por que apenas interceptos aleatórios
   - 6c. O ICC do modelo nulo (50%) — problema real
   - 6d. REML vs ML — qual usar
7. [Modelo B — GEE Logístico](#7-modelo-b--gee-logístico)
   - 7a. GEE vs GLMM — diferença fundamental
   - 7b. Estrutura de correlação exchangeable
   - 7c. Problema crítico: apenas 19 clusters
   - 7d. Candidatos únicos no modelo logístico
8. [Variável sem_emenda (OR=3.57)](#8-variável-sem_emenda--interpretação-crítica)
9. [Efeito deterrence — validade da hipótese](#9-efeito-deterrence--validade-da-hipótese)
10. [Ameaças à identificação causal](#10-ameaças-à-identificação-causal)
11. [Resumo das limitações por ordem de severidade](#11-resumo-das-limitações)
12. [O que a análise pode e não pode afirmar](#12-o-que-a-análise-pode-e-não-pode-afirmar)
13. [Referências](#13-referências)

---

## 1. Escopo da Amostra

### Decisão
Restringir a análise a municípios entre **2.000 e 200.000 habitantes**.

### Justificativa técnica

Municípios muito pequenos (< 2.000 hab.) apresentam problemas específicos:
- **Eleitorado reduzido**: uma única candidatura unânime representa um município inteiro, inflando artificialmente o efeito.
- **Ausência de estrutura partidária formal**: em municípios com menos de 2.000 eleitores, a política local é frequentemente personalista, não partidária, tornando a lógica de "partido aliado no Congresso → repasse → votos" menos aplicável.
- **Outliers eleitorais extremos**: 100% dos votos é comum não por deterrence, mas por ausência de organização política oponente.

Municípios muito grandes (> 200.000 hab.) apresentam outra ordem de problemas:
- **Escala**: o efeito de R$ 10/hab em São Paulo (12M hab.) não é comparável ao efeito em uma cidade de 50.000 hab. — o impacto marginal é diferente.
- **Mídia e informação**: eleitorados grandes têm acesso a múltiplas fontes de informação, diluindo o efeito de repasses.
- **Complexidade das coalizões**: partidos em grandes municípios formam coalizões mais complexas que distorcem a atribuição de mérito.

### Alinhamento com literatura
Montini & Post (2025, SSRN:5254477) encontram que o efeito de transferências tipo pork barrel é concentrado em municípios de médio porte, onde a presença do Estado federal é mais saliente para o eleitorado. O limiar de 200k é consistente com a distinção usada pelo próprio TSE em regras de eleições (turno único abaixo de 200k).

### Possível crítica na defesa
> *"Por que esse corte específico e não outro?"*

**Resposta:** O corte de 200k é amplamente usado na literatura brasileira de política local (e.g., Brollo et al. 2013, Montini & Post 2025) e coincide com regras eleitorais do próprio sistema (TSE). O corte inferior de 2k foi adotado para excluir municípios onde a hipótese de deterrence estratégico é implausível dado o tamanho eleitoral. Ambos os cortes foram pré-especificados no projeto de pesquisa (entregue à orientadora) antes da análise dos dados.

---

## 2. Variável Dependente

### Duas escolhas: por quê?

#### Opção A: `perc_votos` (proporção contínua, 0–1)
**Vantagem:** captura a magnitude do desempenho eleitoral — ganhar com 51% vs. 80% são resultados eleitoralmente distintos.
**Limitação:** exclui os 262 casos de candidatura única (censura em 1.0), que são exatamente os casos de deterrence mais extremo.

#### Opção B: `venceu_com_maioria` (binária, ≥50%)
**Vantagem:** inclui os candidatos únicos (que sempre vencem) e captura o mecanismo de deterrence.
**Limitação crítica:** discutida na Seção 7d.

### Problema conceitual: o que define "desempenho eleitoral"?

A literatura (Samuels 2002, Ames 1995) não tem consenso. Três dimensões são usadas:
1. **Reeleição** (binária): foi reeleito?
2. **Margem de votos** (contínua): qual foi a proporção de votos?
3. **Competitividade** (deterrence): houve oposição?

Neste TCC, o modelo A captura (2) e o modelo B captura (3) — cobertura complementar das três dimensões.

### Problema de censura em 1.0 (Opção A)

Valores de `perc_votos = 1.0` ocorrem quando há candidatura única. Esses valores são **censurados à direita**: não sabemos quantos votos o candidato teria obtido se houvesse oposição — apenas que teria obtido 100%. Incluir esses casos no modelo linear com VD contínua viola a suposição de que a variável dependente segue uma distribuição contínua irrestrita. A exclusão é **metodologicamente correta** para o modelo A.

> **Ref.: Wooldridge (2010), cap. 17 — Tobit and Sample Selection Models.**

---

## 3. Transformação Logarítmica da Variável Explicativa

### O problema sem a transformação

A distribuição de `emendas_pix_per_capita` é fortemente assimétrica à direita (distribuição zero-inflada com cauda pesada):
- ~48% dos municípios têm PIX_pc = 0 (zero exato — partido aliado não alocou nada)
- O restante varia de centavos a R$400+ por habitante
- A presença de outliers extremos faz com que a variância seja dominada por poucos municípios com valores muito altos

Com a variável bruta, o coeficiente estimado de PIX capta principalmente a influência de municípios atípicos, tornando-o instável e estatisticamente insignificante (p = 0,897 no modelo original).

### Justificativa teórica da transformação log

A relação entre transferências fiscais e comportamento eleitoral quase certamente tem **retornos decrescentes**:
- A diferença entre R$0 e R$5/hab é politicamente mais saliente do que entre R$200 e R$205/hab.
- Um eleitorado de baixa renda percebe um repasse de R$10/hab muito mais fortemente do que um eleitorado de alta renda.
- Na literatura econômica, a "função de produção" de votos (Peltzman 1992, Grossman & Helpman 1996) é tipicamente côncava nos recursos alocados.

A transformação `log(1 + x)` converte essa relação multiplicativa em aditiva e linearizável:

```
Modelo implícito: Votos = α × PIX^β × exp(ε)
Log-linearizado:  log(Votos) = log(α) + β × log(PIX) + ε
```

### Por que `log(1+x)` e não simplesmente `log(x)`?

`log(0)` = `-∞`, o que seria problemático para os 48% dos municípios sem repasse. A adição de 1 antes do log garante que zeros mapeiem para 0 na escala log. É uma convenção amplamente usada em econometria de dados de painel com zeros (Autor et al. 2017, Dell & Querubin 2018).

### Limitação importante: Chen & Roth (2024)

Chen & Roth (2024, *Quarterly Journal of Economics*, "Logs with Zeros? Some Problems and Solutions") demonstram que, quando `log(1+Y)` é aplicado à **variável dependente**, o ATE estimado depende da **unidade de medida** de Y — mudar de reais para centavos altera o coeficiente. Esta crítica é **grave** para modelos onde a VD é transformada.

**Porém, no nosso caso, a transformação log é aplicada à VARIÁVEL EXPLICATIVA (X), não à dependente (Y)**. A crítica de Chen & Roth não se aplica diretamente. Para variáveis explicativas, a transformação log tem interpretação econométrica estabelecida: o coeficiente β representa a variação em Y associada a um aumento de 1% em X (elasticidade). Esta interpretação é válida e não depende da unidade de X.

### Como interpretar o coeficiente de log_emenda?

Para a Opção A (linear):
```
β = 0.0164
Interpretação: Um aumento de 1 unidade em log(1 + PIX_pc)
está associado a +1.64 pp na proporção de votos.
```

"1 unidade em log(1+PIX_pc)" corresponde a multiplicar PIX_pc por ~e = 2.718.
Exemplos práticos:
- De R$0 para R$1/hab → Δlog ≈ 0.69 → +1.1 pp nos votos
- De R$1 para R$6/hab → Δlog ≈ 1.79 → +2.9 pp nos votos
- De R$6 para R$54/hab → Δlog ≈ 2.20 → +3.6 pp nos votos

Para a Opção B (logístico):
```
OR = exp(β) = exp(0.454) = 1.575
Interpretação: Um aumento de 1 unidade em log(1 + PIX_pc)
multiplica as odds de vitória por maioria absoluta em 57.5%.
```

### Validação da transformação

1. **Critério prático:** Sem log, p = 0.897 (não significativo). Com log, p < 0.001. Isso indica que a relação real é mais próxima de uma função logarítmica do que linear no PIX bruto.
2. **Critério visual:** Os gráficos de dispersão (fig_scatter_pix_votos.png) mostram que a relação entre log(PIX) e votos é mais linear do que entre PIX_bruto e votos.
3. **Critério de resíduos:** Os resíduos do Modelo A2 têm distribuição mais próxima da normal do que com PIX bruto (verificar QQ-plot no notebook).

### Alternativa não explorada: PPML

Poisson Pseudo-Maximum Likelihood (PPML, Santos Silva & Tenreyro 2006) é uma alternativa teoricamente superior ao log(1+x) para dados com muitos zeros e assimetria. O PPML trata a variável bruta sem transformação e é robusto à heterocedasticidade. **Recomendo como análise de sensibilidade**: rodar PPML com PIX_pc como VI e comparar com os resultados atuais.

---

## 4. Winsorização

### O que é

Winsorização substitui os valores extremos pelos percentis limites:
- Valores abaixo do P1 → substituídos pelo valor do P1
- Valores acima do P99 → substituídos pelo valor do P99

É diferente de **trimming** (que remove os casos) e de **exclusão de outliers** (que pode ser ad hoc).

### Justificativa

A escolha de 1% cada cauda é **convencional em finanças corporativas e econometria empírica** (Winsorize.org; Barber & Lyon 1997). O objetivo não é eliminar valores verdadeiros, mas reduzir a influência desproporcional de casos extremos no estimador OLS/MLE.

### Interação com a transformação log

Aqui há uma nuance importante: **quando a transformação log é aplicada após a winsorização, o efeito da winsorização pode ser redundante**. O log por si só comprime os outliers na escala logarítmica. Por exemplo:
- PIX = R$1.000/hab → log(1+1000) = 6.91
- PIX = R$500/hab → log(1+500) = 6.21
- Diferença: apenas 0.70 unidades — mesmo que R$500/hab vs R$1.000/hab seja economicamente enorme

A winsorização antes do log é uma medida de **prudência adicional**, removendo o impacto dos casos mais extremos antes da compressão logarítmica. Não é errada, mas pode ser redundante.

**Para a defesa:** a justificativa é robustez. Aplicamos ambas as proteções (winsorização + log) para garantir que os resultados não dependam de um punhado de municípios atípicos. Análise de sensibilidade sem winsorização deveria ser realizada (verificar se os coeficientes mudam substancialmente).

---

## 5. Clusterização K-Means como Controles

### O que foi feito

K-Means com k=4 aplicado a 4 variáveis socioeconômicas (IDHM 2010, PIB pc 2021, densidade, alfabetização). As dummies resultantes (cluster_0 a cluster_3) são usadas como controles nos modelos A2 e B1.

### Justificativa

O objetivo é controlar por **heterogeneidade socioeconômica municipal** que pode confundir a relação entre PIX e voto. Municípios mais ricos tendem a ter eleitores mais informados e politicamente independentes; municípios mais pobres podem ser mais suscetíveis a políticas clientelistas.

Usar dummies de cluster em vez das variáveis brutas evita multicolinearidade (IDHM e PIB per capita são altamente correlacionados, r ≈ 0.65) e reduz o número de parâmetros estimados.

### Limitação crítica: viés pós-clusterização

Este é o problema mais sério com o uso de k-means como variável de controle em regressão:

**O k-means atribui municípios a clusters com base nas mesmas variáveis que explicam o desfecho eleitoral.** Se a decisão de qual cluster um município pertence é correlacionada com os resíduos do modelo, os coeficientes das dummies de cluster absorvem variância que deveria ser do efeito de PIX, potencialmente **subestimando** ou **distorcendo** β(log_emenda).

Adicionalmente, o k é escolhido de forma exploratória (método do cotovelo), o que pode configurar **data dredging** implícito — testar diferentes valores de k e escolher o que parece funcionar.

**Mitigações aplicadas:**
1. A escolha de k foi feita em notebook separado (03_clustering.ipynb), antes do notebook de modelagem.
2. Os clusters são baseados em variáveis de nível municipal (IDHM, PIB, densidade, alfabetização) que são instrumentalmente plausíveis como confundidores — não foram selecionadas por correlação com o desfecho.
3. Os resultados são substantivamente robustos: β(log_emenda) passa de 0.0185 (A1, sem clusters) para 0.0164 (A2, com clusters), uma redução de apenas ~11%, sugerindo que o confundimento socioeconômico é moderado.

### Alternativas metodologicamente mais rigorosas

1. **Usar as variáveis brutas com regularização (ridge/lasso):** evita a arbitrariedade do k.
2. **Propensity score matching:** controlar por similaridade socioeconômica sem incluir os controles diretamente na regressão.
3. **Efeitos fixos municipais:** se houvesse dados em painel (anos múltiplos), efeitos fixos absorveriam toda a heterogeneidade municipal invariante no tempo.

**Para a defesa:**
> "Os controles de cluster servem para reduzir confundimento por heterogeneidade socioeconômica. Utilizamos k-means por conveniência e para evitar multicolinearidade entre variáveis altamente correlacionadas. A robustez do coeficiente de log_emenda à inclusão dos clusters (de 0.019 para 0.016, sem mudança na significância) sugere que os resultados não são um artefato da omissão dessas variáveis."

---

## 6. Modelo A — Multinível Linear

### 6a. Justificativa para usar LMM e não OLS simples

Municípios não são observações independentes — municípios do mesmo partido político compartilham:
- O mesmo deputado federal (que alocou o PIX)
- A mesma cultura organizacional partidária
- O mesmo perfil ideológico de candidatos
- Recursos de campanha similares

Esta **dependência intragrupo** viola a suposição de independência dos resíduos do OLS (`ε_i ~ i.i.d.`). Quando os resíduos são correlacionados dentro de grupos, os **erros-padrão do OLS são subestimados**, levando a conclusões de significância estatística que são espúrias.

O modelo de efeitos mistos (LMM) incorpora explicitamente essa estrutura hierárquica:

```
Nível 1 (município i, partido j):
  perc_votos_ij = β₀j + β₁·log_emenda_ij + β₂·sem_emenda_ij + ε_ij

Nível 2 (partido j):
  β₀j = γ₀₀ + u₀j     onde u₀j ~ N(0, τ²)
```

O efeito aleatório `u₀j` captura o fato de que partidos diferentes têm desempenhos eleitorais basais distintos. O PT historicamente performa diferente do PSD em eleições municipais; ignorar isso contaminaria a estimativa de β₁.

**Referência canônica:** Raudenbush & Bryk (2002), *Hierarchical Linear Models*, Sage. Fávero & Belfiore (2024), *Manual de Análise de Dados*, Atlas.

### 6b. Por que apenas interceptos aleatórios e não slopes aleatórios

Um modelo com **slopes aleatórios** permitiria que o efeito de log_emenda variasse entre partidos — o PIX poderia ser mais efetivo para o PT do que para o PSD, por exemplo. Isso seria o modelo "mais rico".

Porém, slopes aleatórios exigem estimação de pelo menos mais 2 parâmetros de variância (a variância do slope e a covariância slope-intercepto). Com apenas **19 grupos** (partidos), isso implica estimar a variância de um processo com base em 19 pontos de dados, o que é insuficiente.

**A regra prática na literatura** (Maas & Hox 2005; Snijders & Bosker 2012) é:
- Interceptos aleatórios: recomendado com ≥ 10 grupos
- Slopes aleatórios: recomendado com ≥ 30 grupos

Com 19 grupos, slopes aleatórios quase invariavelmente resultam em:
- Não-convergência do otimizador
- Estimativas na fronteira do espaço paramétrico (variância = 0)
- Hessiana não positiva definida (instabilidade numérica)

**O que isso significa para a interpretação:** o modelo assume que o efeito de PIX é homogêneo entre partidos (mesma inclinação para todos). Se isso não for verdade, o β estimado é uma média dos efeitos partidários específicos — o que é uma hipótese de trabalho aceitável dado o tamanho da amostra.

**Referências:**
- Maas, C. J. M., & Hox, J. J. (2005). Sufficient sample sizes for multilevel modeling. *Methodology*, 1(3), 86–92.
- Snijders, T. A. B., & Bosker, R. J. (2012). *Multilevel Analysis*, 2ª ed. Sage.

### 6c. O ICC do modelo nulo (~50%): problema real

**O modelo A0 não convergiu (`Converged: No`).**

Isso significa que as estimativas do modelo nulo (ICC = 50%) **não são confiáveis** e não devem ser reportadas como se fossem verdadeiras. A falha de convergência ocorre porque:

1. A variância entre partidos é tão pequena (ou tão mal identificada) que o otimizador não encontra um mínimo global estável.
2. O gradiente permanece elevado (`|grad| = 17.04`) — indicando que o algoritmo BFGS ainda estava longe do ótimo.

**Evidência contrária ao ICC de 50%:** nos modelos A1 e A2 (que convergiram), `Group Var ≈ 0.000`. Isso significa que, **após controlar por log_emenda e sem_emenda, a variância entre partidos desaparece**. A interpretação mais coerente é:

> *A correlação intrapartido observada no modelo nulo era em grande parte explicada pelo fato de que partidos que alocam mais PIX (como PP, MDB, PSD — os maiores) tendem a ter prefeitos aliados com melhor desempenho eleitoral. Quando se controla por log_emenda, não sobra variância significativa a ser atribuída ao partido.*

**Como relatar na defesa:**
> "O modelo nulo apresentou dificuldade de convergência, o que impede a interpretação confiável do ICC estimado. Os modelos A1 e A2, que convergiram, apresentam variância de grupo próxima de zero, sugerindo que o efeito de partido é amplamente mediado pelo volume de Emendas PIX alocadas."

**Solução para o futuro:** usar ML em vez de REML para o modelo nulo, ou usar o método `lbfgs` com reinicializações múltiplas.

### 6d. REML vs ML — qual usar quando

O notebook usa `method='bfgs'`, que é o algoritmo de otimização, não o critério de estimação. O statsmodels `MixedLM.fit()` usa REML por padrão.

**REML (Restricted Maximum Likelihood):**
- Melhor para estimar **componentes de variância** (σ²_u, σ²_e)
- Corrige o viés do ML na estimação das variâncias (MLE subestima as variâncias)
- **Use para:** Modelo final, estimação de ICC, relatório de coeficientes de variância aleatória

**ML (Maximum Likelihood):**
- Melhor para comparar **modelos com diferentes efeitos fixos** via LRT
- O LRT com REML é válido apenas para comparar modelos com os mesmos efeitos fixos
- **Use para:** Comparação A0 vs A1 via LRT quando mudam os efeitos fixos

**Problema no notebook atual:** os LRTs foram calculados com modelos estimados por REML. A comparação A0 vs A1 muda os efeitos fixos (adicionamos log_emenda e sem_emenda), portanto o LRT com REML é **tecnicamente inválido**. Para LRT entre modelos com diferentes efeitos fixos, deve-se usar ML.

**Na prática:** com n = 4.935, a diferença entre ML e REML é pequena, e os LRTs provavelmente chegam à mesma conclusão. Mas é uma crítica metodológica válida que merece menção nas limitações.

> **Ref.:** Pinheiro, J. C., & Bates, D. M. (2000). *Mixed-Effects Models in S and S-PLUS*. Springer, cap. 2.

---

## 7. Modelo B — GEE Logístico

### 7a. GEE vs GLMM — diferença fundamental

Esta é talvez a distinção mais importante e frequentemente mal compreendida em modelos para dados agrupados.

**GLMM (Generalized Linear Mixed Model) — modelo condicional:**
```
logit[P(Y_ij = 1 | X_ij, u_j)] = β₀ + β₁X_ij + u_j
```
O efeito β₁ é interpretado *condicionalmente ao partido*: "Para um dado partido, mantendo o efeito aleatório do partido constante, um aumento de 1 unidade em log_emenda aumenta as log-odds de vitória em β₁."

**GEE (Generalized Estimating Equations) — modelo marginal/populacional:**
```
logit[P(Y_ij = 1 | X_ij)] = β₀ + β₁X_ij
(correlação intrapartido tratada como estrutural, não como efeito aleatório)
```
O efeito β₁ é interpretado *marginalmente na população*: "Na população de municípios, um aumento de 1 unidade em log_emenda está associado a β₁ unidades de aumento nas log-odds médias de vitória."

**Por que essa diferença importa para a pergunta de pesquisa?**

A pergunta do TCC é sobre o efeito **médio** das Emendas PIX nos municípios brasileiros — não sobre o efeito condicional "dentro de um partido específico". Portanto, a interpretação **marginal/populacional** do GEE é mais alinhada com a pergunta científica do que a interpretação condicional do GLMM.

> *"On average, in the population of Brazilian municipalities, are PIX transfers associated with higher probability of mayoral victory by absolute majority?"* — GEE responde isso diretamente.

**Referências fundamentais:**
- Zeger, S. L., & Liang, K.-Y. (1986). Longitudinal data analysis for discrete and continuous outcomes. *Biometrics*, 42, 121–130.
- Liang, K.-Y., & Zeger, S. L. (1986). Longitudinal data analysis using generalized linear models. *Biometrika*, 73, 13–22.
- Hardin, J. W., & Hilbe, J. M. (2013). *Generalized Estimating Equations*, 2ª ed. Chapman & Hall/CRC.

### 7b. Estrutura de correlação exchangeable

O GEE precisa de uma suposição sobre a estrutura de correlação entre observações no mesmo cluster. Usamos **exchangeable** (uniforme).

**O que assume:** toda e qualquer correlação entre dois municípios do mesmo partido é igual. Formalmente:
```
Cor(Y_ij, Y_ij') = ρ   para todos i ≠ i' dentro do mesmo partido j
```

**Quando é adequada:**
- Quando as observações dentro do cluster não têm ordem natural que geraria correlações diferentes (ex.: série temporal, onde observações próximas são mais correlacionadas).
- No nosso caso, municípios dentro de um partido não têm ordem natural — são um conjunto de cidades, e a correlação entre Porto Alegre e Fortaleza (ambas ex-PT) deve ser igual à correlação entre dois municípios menores do mesmo partido. A estrutura exchangeable é, portanto, **razoável**.

**Alternativas:**
- **Independence:** ignora a correlação (equivale a logística simples com SE corrigidos) — muito conservadora.
- **Unstructured:** estima cada par de correlações separadamente — impossível com clusters de tamanhos desiguais (838 municípios no PSD!).
- **AR(1):** adequada para séries temporais, não para dados cross-section agrupados.

A robustez do GEE à misspecificação da estrutura de correlação (via estimador sanduíche) significa que mesmo que a correlação real não seja exatamente exchangeable, os coeficientes ainda são consistentes — apenas os erros-padrão podem ser levemente distorcidos.

### 7c. Problema crítico: apenas 19 clusters

Este é o ponto metodológico mais vulnerável do modelo B.

**O estimador sanduíche (Liang-Zeger) de GEE é assintoticamente consistente mas com viés em amostras finitas.** Estudos de simulação mostram:

- Com ≥ 40 clusters: erros-padrão são confiáveis.
- Com 20–39 clusters: possível viés de 10–20% na variância estimada (erros-padrão subestimados).
- Com < 20 clusters: viés substancial, testes de hipóteses potencialmente inválidos.

Com nossos **19 clusters**, estamos ligeiramente abaixo do limiar problemático. Isso significa que os p-valores calculados podem ser **anticonservadores** — rejeitamos H₀ mais frequentemente do que o correto.

**Magnitudes de nossos efeitos:** p < 0.001 com z = 11.07 para log_emenda. Mesmo com correção de viés de 20-30% nos erros-padrão (o que é muito conservador), o z seria ~7.7, ainda p < 0.001. Portanto, a conclusão de significância estatística é **robusta** mesmo considerando esse problema.

**Correções disponíveis (mas não implementadas):**
- **Mancl-DeRouen (2001):** correção para SE do GEE com poucos clusters.
- **Pan (2001):** variante da correção de Mancl-DeRouen.
- **Bootstrap clustered:** reamostrar partidos com replacement para obter SE empíricos.

**Para a defesa:**
> "Reconhecemos que o estimador sanduíche do GEE tem propriedades assintóticas que podem ser imperfeitas com 19 clusters. Porém, a magnitude do efeito (z = 11.07) e seu intervalo de confiança (OR 1.45–1.71) são tão distantes de 1 que, mesmo aplicando correções conservadoras de Mancl-DeRouen, a conclusão de significância seria mantida."

**Referências:**
- Mancl, L. A., & DeRouen, T. A. (2001). A covariance estimator for GEE with improved small-sample properties. *Biometrics*, 57(1), 126–134.
- Huang, F. L. (2022). Analyzing cross-sectionally clustered data using generalized estimating equations. *Journal of Educational and Behavioral Statistics*, 47(1), 64–97.

### 7d. Candidatos únicos no modelo logístico: o problema de separação

**Esta é a crítica mais profunda ao Modelo B.**

No Modelo B, incluímos os 262 municípios com candidatura única (perc_votos = 1.0). Para esses municípios:
- `venceu_com_maioria = 1` **por definição** — não há variação no desfecho.
- `candidato_unico = TRUE` determina perfeitamente `venceu_com_maioria = 1`.

**O problema:** embora `candidato_unico` não seja um preditor no modelo (não incluímos essa variável na fórmula), ela é **implicitamente correlacionada com log_emenda** — municípios com candidatura única tendem a ter maior PIX (como confirmado pela análise descritiva: 9.1% vs 3.5% no Q4 vs Q1). Isso cria um mecanismo indireto:

```
log_emenda (alto) → candidato_unico = 1 → venceu_com_maioria = 1
```

Parte do efeito de `log_emenda` sobre `venceu_com_maioria` pode ser simplesmente reflexo de que municípios com muito PIX têm mais candidaturas únicas — que por definição são vitorias com maioria. Isso não é estimação do efeito de PIX sobre *o resultado de uma eleição contestada* — é parcialmente estimação da correlação entre PIX e *se haverá uma eleição contestada*.

**O que significa para a interpretação:**

O OR = 1.57 do Modelo B não pode ser interpretado apenas como "PIX melhora o desempenho eleitoral em eleições competitivas". Ele mistura dois mecanismos:
1. **Efeito direto nas eleições competitivas:** maior PIX → maior proporção de votos (Modelo A)
2. **Efeito dissuasório:** maior PIX → mais candidaturas únicas → mais vitórias por maioria (efeito deterrence)

**Esta é na verdade a interpretação pretendida** — capturar ambos os mecanismos. O Modelo B é honesto sobre isso: ele mede o efeito total de PIX sobre a probabilidade de vitória por maioria absoluta, **incluindo** o canal de deterrence.

**Framing correto para a defesa:**
> "O Modelo B deliberadamente captura o efeito total de Emendas PIX sobre a vitória por maioria absoluta, *incluindo* o mecanismo de deterrence. Municípios com alto volume de PIX têm maior probabilidade de vitória por maioria não apenas porque o prefeito recebe mais votos nas urnas, mas também porque oponentes em potencial podem se abster de competir. O Modelo A, por sua vez, isola apenas o primeiro mecanismo, ao excluir as candidaturas únicas. Os dois modelos são complementares e endereçam diferentes aspectos da mesma pergunta."

---

## 8. Variável sem_emenda — Interpretação Crítica

### O achado
`sem_emenda = 1` para municípios onde o PIX da aliança partidária é zero.
Resultado: **OR = 3.57** (Modelo B1) — municípios sem qualquer repasse PIX do partido aliado têm odds 257% maiores de vitória por maioria.

### Por que esse resultado é contra-intuitivo?

A hipótese padrão seria: mais PIX → mais probabilidade de vitória. Então municípios com ZERO PIX deveriam ter *menor* probabilidade de vitória. Por que têm maior?

### Hipóteses explicativas

**Hipótese 1 — Viés de seleção (mais provável):**
Municípios onde o partido do prefeito eleito não tem nenhum deputado federal aliado que enviou PIX podem ser **fortalezas políticas** — o prefeito ganhou com margem tão confortável que nem precisou de PIX. Partidos que dominam uma cidade com 70%+ dos votos não precisam de repasses para garantir a vitória. A ausência de PIX é correlacionada com domínio político, não com fraqueza.

**Hipótese 2 — Multicolinearidade com log_emenda:**
`sem_emenda = 1` implica `log_emenda = 0` (pois log(1+0) = 0). Portanto, `sem_emenda` e `log_emenda` são colineares de forma estrutural para os 48% dos municípios sem emenda. Isso pode criar instabilidade na estimação dos dois coeficientes simultaneamente.

**Hipótese 3 — Efeito de partidos menores:**
Pequenos partidos que não têm presença no Congresso (sem deputados para enviar PIX) podem ter prefeitos em municípios onde a política é mais personalista e menos dependente de recursos federais — municípios onde um prefeito carismático ganha com maioria independentemente de repasses.

### Recomendação metodológica

A inclusão de `sem_emenda` como variável de controle é tecnicamente adequada mas **a interpretação do seu coeficiente é problemática** por essas razões. Para a defesa:

> "O coeficiente de sem_emenda captura o efeito de pertencer ao grupo de municípios sem repasse PIX do partido aliado. O OR elevado (3.57) provavelmente reflete viés de seleção: municípios sem nenhum deputado aliado enviando PIX são aqueles onde o partido já domina eleitoralmente sem precisar de recursos externos. Não interpretamos esse coeficiente como efeito causal da ausência de PIX."

---

## 9. Efeito Deterrence — Validade da Hipótese

### Evidência empírica no TCC

- **Q4 vs Q1:** 9.1% vs 3.5% de candidaturas únicas — diferença de +5.6 pp (2.6x mais frequente no quartil superior)
- **Folha de S.Paulo (2024):** 12 candidaturas únicas entre os 116 municípios mais beneficiados
- **Taxa de maioria:** 93.1% no Q4 vs 81.2% no Q1

### Referências de suporte na literatura brasileira

- **Brollo et al. (2013, AER):** Mostram que maiores transferências federais aumentam a probabilidade de reeleição do prefeito aliado e reduzem a qualidade dos oponentes que se candidatam.
- **Montini & Post (2025, SSRN:5254477):** Específico para Emendas PIX, encontra associação entre volume de repasses e dominância eleitoral.
- **De Janvry et al. (2012):** Análise de transferências condicionais e comportamento eleitoral no Brasil — achados similares de deterrence via recursos públicos.

### Limitação da hipótese de deterrence

A **identificação causal do efeito de deterrence requer mais do que correlação**. O mecanismo completo seria:

```
[Deputado envia PIX] → [Eleitorado percebe e atribui mérito ao prefeito aliado]
→ [Oponentes reconhecem vantagem do prefeito] → [Oponentes desistem de competir]
```

Cada elo dessa cadeia pode ser questionado:
1. **Atribuição de mérito:** o eleitorado sabe que o prefeito foi o responsável pelo PIX? Em municípios pequenos com mídia limitada, isso é incerto.
2. **Decisão estratégica dos oponentes:** candidatos podem desistir de competir por outras razões (custos de campanha, incumbência, falta de recursos próprios).
3. **Reverso causal:** partidos dominantes em uma cidade têm mais deputados, que enviam mais PIX — a causalidade pode ser inversa.

**Conclusão:** a hipótese de deterrence é **consistente com os dados** mas não pode ser **comprovada causalmente** com o design observacional atual. A narrativa do deterrence é um mecanismo plausível, não uma prova.

---

## 10. Ameaças à Identificação Causal

Esta seção é essencialmente um capítulo de **limitações do estudo** que toda banca irá perguntar.

### 10.1 Endogeneidade / Reverso Causal

**Ameaça:** Deputados federais alocam mais PIX para municípios onde seu partido já tem prefeito eleitoralmente forte. A causalidade pode ser:

```
Município politicamente forte → Deputado aliado envia mais PIX (para "regar a planta")
```

Em vez de:
```
Deputado envia PIX → Município passa a ter prefeito mais forte
```

**Evidência dessa ameaça:** a literatura (Samuels 2002, Ames 1995) mostra que deputados brasileiros usam recursos para manter bases eleitorais já existentes, não para conquistar novas. Isso implica que a correlação observada entre PIX e votos pode ser espúria — ambos são determinados por uma terceira variável (força política do partido na cidade).

**Por que não podemos resolver com os dados disponíveis:**
Resolução ideal: **Variável Instrumental (IV)** — encontrar algo que determine a alocação de PIX mas não tenha efeito direto sobre votos, exceto via PIX. Exemplos teóricos na literatura: posição do deputado em comitê de orçamento, regras de alocação por fórmula. Não dispomos dessas informações neste estudo.

**Por que o problema pode ser menor do que parece:**
A transformação log garante que estamos capturando variação na intensidade do PIX, não apenas presença/ausência. Mesmo que municípios politicamente fortes recebam mais PIX, se a relação entre intensidade de PIX e votos for positiva *dentro* desses municípios, o efeito estimado tem algum conteúdo causal.

### 10.2 Variáveis Omitidas

Variáveis correlacionadas com PIX *e* com votos que não controlamos:
- **Qualidade do gestor:** prefeitos mais competentes executam melhor os recursos do PIX e são reeleitos por mérito.
- **Conjuntura econômica local:** boom de commodities em uma região pode aumentar votos e atrair mais investimento político federal.
- **Timing dos repasses:** PIX enviado no pré-eleitoral vs. no início do mandato tem impactos eleitorais diferentes — não controlamos isso.

### 10.3 Definição do Grupo de Tratamento (partido aliado)

**Decisão metodológica questionável:** usamos apenas as emendas dos deputados federais do **mesmo partido do prefeito eleito**. Mas:
- Deputados de partidos aliados na coligação também podem ter enviado PIX.
- O prefeito eleito em 2024 pode ter sido eleito por um partido diferente do que em 2020 (mudança partidária).
- A aliança entre prefeito e deputado pode ser mais fluida do que a filiação partidária sugere.

Idealmente, o "PIX aliado" deveria ser definido por alinhamento de coligação ou por declaração explícita de apoio, não apenas por partido. Isso é uma limitação dos dados disponíveis (CGU e TSE não fornecem dados de coligação com essa granularidade).

### 10.4 Agregação temporal (2020–2024)

Usamos o PIX acumulado de 5 anos (2020–2024). Isso mistura:
- PIX do início do mandato (2021): impacto difuso, difícil de atribuir ao prefeito
- PIX pré-eleitoral (2023–2024): máximo impacto eleitoral esperado
- PIX em resposta a desastres ou emergências: não é clientelismo, mas conta nos dados

A agregação suaviza diferenças de timing que podem ser eleitoralmente relevantes.

---

## 11. Resumo das Limitações por Ordem de Severidade

| # | Limitação | Severidade | Impacto nos resultados | Mitigação |
|---|---|---|---|---|
| 1 | Endogeneidade / reverso causal | **Alta** | Superestimação do efeito | Análise observacional — não resolvida |
| 2 | GEE com apenas 19 clusters | **Média-Alta** | SE subestimados, mas efeito tão grande que conclusão mantida | Reportar como limitação; z=11 mesmo com 30% viés SE |
| 3 | LRT com REML para comparação de FE | **Média** | LRT A0→A1 pode ser levemente inválido | Refazer com ML para confirmar |
| 4 | ICC do modelo nulo não convergiu | **Média** | ICC 50% não confiável | Usar Group Var≈0 de A1/A2 como evidência |
| 5 | Candidatos únicos em modelo logístico | **Média** | Efeito mistura mecanismo direto + deterrence | Interpretação dual — deliberada |
| 6 | sem_emenda OR=3.57 | **Média** | Seleção, não efeito causal | Não interpretar causalmente |
| 7 | K-means como controles | **Baixa** | β(log_emenda) robusta à inclusão (0.019→0.016) | Análise de sensibilidade sem clusters |
| 8 | log(1+x) e zeroes | **Baixa** | Padrão da literatura — Chen & Roth não se aplica à VI | Rodar sensibilidade com PPML |
| 9 | Winsorização 1% | **Muito Baixa** | Redundante com log, mas harmless | Rodar sem winsorização |
| 10 | Dados socioeconômicos defasados | **Muito Baixa** | Clusters baseados em dados de 2010 | Usar apenas como controles de perfil, não como mensuração atual |

---

## 12. O que a Análise Pode e Não Pode Afirmar

### Pode afirmar ✓

1. **Associação positiva e estatisticamente robusta** entre volume de Emendas PIX per capita alocadas pelo deputado federal do mesmo partido do prefeito e o desempenho eleitoral do prefeito em 2024 (p < 0.001 em todos os modelos).

2. **Consistência do efeito:** resultado significativo em dois modelos com variáveis dependentes diferentes (contínua e binária), duas estratégias de estimação diferentes (LMM e GEE) e com/sem controles socioeconômicos.

3. **Evidência descritiva do efeito deterrence:** municípios no quartil superior de PIX têm 2.6x mais candidaturas únicas e +11.9 pp na taxa de vitória por maioria.

4. **Rejeição da hipótese nula de ausência de efeito** com altíssimo grau de confiança (considerando as limitações conhecidas do número de clusters no GEE).

### Não pode afirmar ✗

1. **Causalidade:** não podemos afirmar que Emendas PIX *causam* melhor desempenho eleitoral. A endogeneidade não é resolvida.

2. **Mecanismo específico:** os dados não distinguem entre (a) eleitorado recompensa prefeito por trazer recursos, (b) PIX financia campanha do prefeito, (c) PIX deterrence oponentes, (d) deputados alocam mais PIX para prefeitos que já são fortes.

3. **Generalização para outros contextos:** o efeito pode ser específico às eleições de 2024 e ao formato particular das Emendas PIX (obrigatórias, sem destinação vinculada).

4. **Magnitude precisa:** dado o problema de endogeneidade, a magnitude dos coeficientes (OR 1.57, β 0.016) pode ser uma superestimação do efeito causal real.

---

## 13. Referências

- Ames, B. (1995). Electoral rules, constituency pressures, and pork barrel. *Journal of Politics*, 57(2), 324–343.
- Box, G. E. P., & Cox, D. R. (1964). An analysis of transformations. *Journal of the Royal Statistical Society B*, 26(2), 211–252.
- Brollo, F., Nannicini, T., Perotti, R., & Tabellini, G. (2013). The political resource curse. *American Economic Review*, 103(5), 1759–1796.
- Chen, J., & Roth, J. (2024). Logs with zeros? Some problems and solutions. *Quarterly Journal of Economics*, 139(2), 891–936. https://doi.org/10.1093/qje/qjad054
- Fávero, L. P., & Belfiore, P. (2024). *Manual de Análise de Dados*. Atlas.
- Hardin, J. W., & Hilbe, J. M. (2013). *Generalized Estimating Equations*, 2ª ed. Chapman & Hall/CRC.
- Heckman, J. J. (1979). Sample selection bias as a specification error. *Econometrica*, 47(1), 153–161.
- Huang, F. L. (2022). Analyzing cross-sectionally clustered data using generalized estimating equations. *Journal of Educational and Behavioral Statistics*, 47(1), 64–97.
- Liang, K.-Y., & Zeger, S. L. (1986). Longitudinal data analysis using generalized linear models. *Biometrika*, 73(1), 13–22.
- Maas, C. J. M., & Hox, J. J. (2005). Sufficient sample sizes for multilevel modeling. *Methodology*, 1(3), 86–92.
- Mancl, L. A., & DeRouen, T. A. (2001). A covariance estimator for GEE with improved small-sample properties. *Biometrics*, 57(1), 126–134.
- Montini, M., & Post, A. (2025). Size matters: Pork politics and state presence in Brazilian municipalities. SSRN Working Paper 5254477.
- Pinheiro, J. C., & Bates, D. M. (2000). *Mixed-Effects Models in S and S-PLUS*. Springer.
- Raudenbush, S. W., & Bryk, A. S. (2002). *Hierarchical Linear Models*, 2ª ed. Sage.
- Samuels, D. J. (2002). Pork barreling is not credit claiming or advertising: campaign finance and the sources of the personal vote in Brazil. *Journal of Politics*, 64(3), 845–863.
- Santos Silva, J. M. C., & Tenreyro, S. (2006). The log of gravity. *Review of Economics and Statistics*, 88(4), 641–658.
- Snijders, T. A. B., & Bosker, R. J. (2012). *Multilevel Analysis*, 2ª ed. Sage.
- Wooldridge, J. M. (2010). *Econometric Analysis of Cross Section and Panel Data*, 2ª ed. MIT Press.
- Zeger, S. L., & Liang, K.-Y. (1986). Longitudinal data analysis for discrete and continuous outcomes. *Biometrics*, 42(1), 121–130.

---

*Documento criado com Claude Code — Fevereiro 2026*
