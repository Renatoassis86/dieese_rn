# Dicionário de Dados - PAA (Programa de Aquisição de Alimentos)

Este dicionário descreve as variáveis das bases de execução do PAA, conforme documentação do MDS.

## 1. Base: Execução Financeira – Compra com Doação Simultânea (Termo de Adesão)
*Frequência: Mensal. Cobertura: 2024-2026.*

| Variável | Descrição |
| :--- | :--- |
| `Código IBGE` | Código da unidade executora (município/estado). |
| `UF` | Sigla do estado. |
| `Estado/Município` | Nome da unidade executora. |
| `Tipo adesão` | Estadual ou municipal. |
| `Ano da pactuação` | Ano do aporte de recursos financeiros. |
| `Nº do plano operacional` | Identificador do Plano Operacional. |
| `Vigência` | Data de encerramento do Plano. |
| `Valor pactuado` | Recursos financeiros totais pactuados. |
| `Valor pago` | Recursos financeiros efetivamente pagos. |
| `% de Execução` | Proporção do valor pago sobre o pactuado. |
| `Origem do orçamento` | Recurso ordinário MDS, crédito extraordinário ou emenda. |
| `Status` | Liberados, bloqueados ou cancelados. |
| `Público atendido` | Amplo ou específico (indígenas, quilombolas, etc.). |
| `Data de referência` | Mês da folha de pagamento. |

## 2. Base: Municípios com Adesão ao PAA
*Cobertura: 2022-2026.*

| Variável | Descrição |
| :--- | :--- |
| `codigo_ibge` | Código IBGE do município. |
| `anomes_s` | Ano e mês de referência. |
| `sigla_uf` | UF do município. |
| `municipio` | Nome do município. |
| `paa_indicador_adesao_municipio_i` | Indicador binário de adesão. |

## 3. Base: Execução Geral (Série Histórica 2011-2025)
*Dados agregados por município.*

| Variável | Descrição |
| :--- | :--- |
| `agricultores_fornec_paa_i` | Número de agricultores familiares fornecedores. |
| `recur_pagos_agricul_paa_f` | Recursos financeiros totais pagos aos agricultores. |

## 4. Base: Modalidades Específicas
*   **Leite (2021-2025)**:
    *   `paa_qtd_agricul_familiar_exec_incentivo_leite_i`: Qtd de fornecedores.
    *   `paa_vlr_pago_exec_incentivo_leite_d`: Valor pago.
    *   `paa_qtd_alim_adquiridos_exec_incentivo_leite_i`: Litros de leite.
*   **Compra com Doação Simultânea (2011-2025)**:
    *   `paa_qtd_agricul_familiar_modal_compra_doacao_simul_i`: Qtd de fornecedores.
    *   `paa_vlr_pago_exec_compra_doacao_simul_d`: Valor pago.
    *   `paa_qtd_alim_adquiridos_exec_compra_doacao_simul_d`: Quilos de alimentos.

## 5. Base: Perfil Social (Sexo)
| Variável | Descrição |
| :--- | :--- |
| `paa_qtd_agricul_familiar_sexo_masculino_i` | Qtd fornecedores masculinos. |
| `paa_qtd_agricul_familiar_sexo_feminino_i` | Qtd fornecedores femininos. |
| `paa_qtd_agricul_familiar_sem_info_sexo_i` | Qtd sem informação de sexo. |

---
*Fonte: Transcrição de docs/VARIÁVEIS PAA.docx e Metadados MDS.*
