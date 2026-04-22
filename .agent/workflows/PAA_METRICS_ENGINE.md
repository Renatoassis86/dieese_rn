# Motor de Métricas do PAA — Observatório Rural RN

Este documento é a **Referência Mestra** para todos os scripts de Banco de Dados, APIs e Painéis do BI vinculados ao **Diagnóstico do Mercado Institucional (PAA)**. 

### 1. Fontes de Dados (As 11 Bases Oficiais do Governo)
Todo o ecossistema de dados deve compulsoriamente buscar dados do MiSocial e formatar no banco nas seguintes frentes:
1. **Termo de Adesão (Exec. Financeira)**: Pactuado, Pago, Não executado, % de execução (Pago/Pactuado), Origem do Orçamento, Público (Geral/Específico).
2. **Municípios Aderidos**: Captura de CNPJs/Cidades via IBGE.
3. **Execução Geral**: Volume bruto em moeda e quantitativo macro de produtores inscritos.
4. **Agric. Familiares por Gênero**: Estratificação de Masculino, Feminino e Não-informado.
5. **Modalidade: Compra c/ Doação Simultânea**: Volumes físicos (Kg) e financeiros (R$).
6. **Modalidade: Leite**: Volumes físicos (Litros) e numéricos (Produtores).
7. **Modalidade: Compra c/ Doação Simultânea (Apenas pessoas)**: Série de 2011 a 2025.
8. **Modalidade: Incentivo Prod. Leite (Apenas pessoas)**: Série de 2011 a 2025.
9. **Modalidade: Compra Direta**: Série de 2011 a 2017.
10. **Modalidade: Apoio Formação de Estoques**: Série de 2011 a 2019.
11. **Modalidade: Aquisição de Sementes**: Série de 2015 a 2020.

---

### 2. Dicionário de Variáveis Derivadas (Cruciais para BI e Estudos)
Além dos dados absolutos, os sistemas devem calcular preventivamente ou em tempo de execução (`api.js`) as seguintes métricas relativas (storytelling):

* **Variação Percentual Anual (YoY - Year over Year)**: 
  * `(Valor_AnoAtual - Valor_AnoAnterior) / Valor_AnoAnterior * 100` -> (Ex: "Crescimento de +14% nos investimentos em relação ao ano passado")
* **Share / Percentual de Distribuição Territorial**:
  * `(Produtores_Regiao_X / Total_Produtores_Estado) * 100` -> (Ex: "O Seridó concentra 12% dos agricultores familiares do Estado")
* **Índice de Execução de Metas**: 
  * `(Valor Pago / Valor Pactuado) * 100` -> Métrica vitalícia para julgar se a política é eficiente.
* **Capilaridade Geográfica**: 
  * Total de municípios que acessaram *vs* (167). (Ex: "Atuação de 80.2% no solo Potiguar")
* **Ticket Médio por Produtor**:
  * `Valor Total Pago / Número de Produtores` -> (Ex: "R$ 4.200 pagos em média por família / ano").
* **Proporção de Gênero**:
  * `(Mulheres / Total_Produtores) * 100` -> Fundamental para evidenciar o papel da mulher rural.

---

### 3. Matriz de Visualização Obrigatória (Checklist p/ Views Estáticas & Dashboards)
Qualquer representação visual do estudo de PAA deve possuir:
- [x] O montante total em Série Histórica consolidada.
- [x] Ranking Geográfico das 10 macros-regiões (Territórios).
- [x] Mapa com sinalização de calor ou bolhas (Capilaridade).
- [x] Gráfico particionado cruzando Modalidades entre si.
- [x] Comparação RN vs Nordeste.
- [x] Indicadores Derivados em caixas ou texto (YoY%, Percentuais femininos, Execução do Termo).
