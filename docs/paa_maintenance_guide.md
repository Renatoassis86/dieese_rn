# Guia de Sustentabilidade: Dimensão PAA

Este documento detalha o funcionamento da integração e como garantir que os dados do PAA permaneçam atualizados.

## 1. Fonte da Verdade (Pipeline)
A plataforma consome dados da tabela `paa_master` no Supabase. Esta tabela é alimentada pelo script exaustivo:
`src/extraction/paa_sync_automated.py`

## 2. Métricas Extraídas (Cobertura 100%)
Conforme solicitado, o pipeline agora captura:
- **Execução Financeira**: Valor total pago, Valor Leite, Valor Compra com Doação.
- **Execução Física**: Famílias beneficiárias, Litros de Leite, Quilos de Alimentos.
- **Perfil Social**: Recorte de gênero (Gênero Feminino/Masculino).
- **Territorial**: Vinculação automática aos 10 territórios do RN via código IBGE.

## 3. Como Atualizar (Manutenção)
Para atualizar a plataforma com os novos dados mensais do MDS:
1. Certifique-se que o ambiente Python está ativo: `.\.venv\Scripts\activate`
2. Execute o comando: `python src/extraction/paa_sync_automated.py`
3. O script realiza a extração do Nordeste completo e realiza o "Upsert" (Merge) no Supabase.

## 4. Visualização no BI
Os gráficos de **Série Temporal** e **Territórios** no dashboard são gerados dinamicamente com base nesta tabela. 
- Filtros de **Público Feminino** e **Volumes (Kg/L)** podem ser adicionados ao BI a qualquer momento consumindo as novas colunas `quilos_alimentos` e `litros_leite`.

---
*Documentação gerada em 22/04/2026 para o Observatório Rural RN.*
