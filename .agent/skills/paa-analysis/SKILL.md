# Skill: PAA Analysis Protocol (RN)

Este documento define o protocolo oficial de análise dos dados do Programa de Aquisição de Alimentos (PAA) para o Observatório Rural do Rio Grande do Norte.

## 1. Escopo de Dados
*   **Abrangência Geográfica**: 
    1.  Brasil (Total para Contexto)
    2.  Nordeste (Comparativo por Estado)
    3.  Rio Grande do Norte (Geral)
    4.  RN Territorial (10 Regiões)
    5.  RN Municipal (167 Municípios)
*   **Período Temporal**: Máximo disponível para cada variável (Série histórica 2011-2026).

## 2. Matriz de Métricas (Key Performance Indicators)
Conforme documento `VARIÁVEIS PAA.docx`, as métricas obrigatórias são:

| Métrica | Nome da Variável (API) | Descrição |
| :--- | :--- | :--- |
| **Pactuação** | `valor_pactuado`, `status` | Recursos financeiros totais pactuados via Termo de Adesão. |
| **Execução Financeira** | `recur_pagos_agricul_paa_f` | Recursos efetivamente pagos aos agricultores. |
| **Execução Física** | `agricultores_fornec_paa_i` | Número de famílias/agricultores fornecedores ativos. |
| **Perfil Social** | `paa_qtd_agricul_f_sexo_f_i` | Participação de mulheres no programa. |
| **Modalidade Leite** | `paa_vlr_pago_exec_leite_d` | Recurso específico da modalidade Leite. |
| **Capilaridade** | `% Mun. Atendidos` | Proporção de municípios com execução ativa no território. |
| **Ticket Médio** | `Vlr Pago / Agricultores` | Valor médio recebido por família fornecedora. |

## 3. Divisão Territorial (RN)
A agregação deve seguir estritamente os **10 Territórios** definidos no "Seminário Territorial da Política Pública do Trabalho":
1. Seridó | 2. Alto Oeste | 3. Agreste Litoral Sul | 4. Mato Grande | 5. Assú-Mossoró | 6. Potengi | 7. Trairi | 8. Sertão Central Cabugi e Litoral Norte | 9. Sertão do Apodi | 10. Terras Potiguares.

## 4. Estrutura de Saída (BI-Ready)
Os arquivos devem ser gerados em formato `.xlsx` com abas separadas por nível de agregação, preparados para ingestão em banco de dados:
- Aba `1. Nordeste Comparativo`
- Aba `2. RN Geral`
- Aba `3. RN Territorial`
- Aba `4. RN Municipal (Série Completa)`

---
*Protocolo estabelecido em 22/04/2026.*
