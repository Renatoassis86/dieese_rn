# Plano Tabular - Observatório Rural do RN

Este documento descreve a organização dos dados, variáveis e tabelas para o Observatório Socioeconômico da Agricultura Familiar e Economia Solidária do Rio Grande do Norte.

## 1. Estrutura de Entidades

Para garantir a escalabilidade e a integração dos dados (PAA, Censo Agro, RAIS, etc.), os dados serão organizados nos seguintes níveis:

### 1.1. Geográfico (Territorial)
*   **Municípios**: Tabela base com Código IBGE, Nome, Microrregiao, Mesorregiao e Território da Cidadania.
*   **Territórios**: Agrupamentos de municípios definidos pelas políticas de desenvolvimento rural.

### 1.2. Programas e Políticas Públicas (Detalhes)

#### A. PAA (Programa de Aquisição de Alimentos)
*   **Bases Históricas (2011-2026):**
    *   **Execução Geral**: `agricultores_fornec_paa_i`, `recur_pagos_agricul_paa_f`.
    *   **Perfil Social**: Quantidade por sexo (`masculino`, `feminino`, `sem_informação`).
    *   **Modalidades Específicas**:
        *   **Leite**: `paa_vlr_pago_exec_incentivo_leite_d`, `paa_qtd_alim_adquiridos_exec_incentivo_leite_i` (Litros).
        *   **Compra com Doação Simultânea**: `paa_vlr_pago_exec_compra_doacao_simul_d`, `paa_qtd_alim_adquiridos_exec_compra_doacao_simul_d` (Quilos).
        *   **Outras**: Compra Direta, Apoio à Formação de Estoques, Aquisição de Sementes.
    *   **Adesão Municipal**: Indicador de adesão por município e ano.
    *   **Execução Termo de Adesão (MDS)**: Valor pactuado vs. Valor pago, Status, público atendido.

## 2. Organização do Data Lake (Local)

Os dados serão organizados no diretório `data/` seguindo a arquitetura Medalhão:

*   `data/raw/`: Dados originais (Ex: `municipios_rn.csv`, planilhas PAA).
*   `data/processed/`: Dados limpos e padronizados.
*   `data/final/`: Tabelas consolidadas (ex: `view_municipio_paa_consolidado`).

## 3. Próximos Passos de Extração

1.  **IBGE - Censo Agro 2017**: Extrair variáveis de estabelecimentos e produção.
2.  **Consolidação PAA**: Criar script para unificar as diversas bases do PAA descritas acima em uma única visão temporal por município.
3.  **Cruzamento RAIS/CADSOL**: Identificar vínculos de economia solidária.

---
*Documento em construção. Última atualização: 2026-04-21*
