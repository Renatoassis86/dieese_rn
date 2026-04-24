# Caderno Metodológico: PNAD SOL (Trabalho e Renda Rural RN)

## 1. Estrutura do Estudo
Este estudo utiliza microdados da PNAD Contínua para diagnosticar a economia solidária e o trabalho rural no RN entre 2012 e 2025.

## 2. Dicionário de Variáveis Derivadas
(Consolidado conforme instruções do prompt anterior)

## 3. Fluxo de Dados
- **Download**: Temporários em `download_pnad/`.
- **Bronze**: Arquivos .txt originais (se salvos).
- **Silver**: Arquivos .parquet limpos.
- **Gold**: Bases harmonizadas com as 54 métricas aplicadas.
- **Results**: CSVs consolidados para dashboard.

## 4. Notas Técnicas
As proxies de Economia Solidária baseiam-se na combinação de:
- Posição na Ocupação (VD4009)
- Registro de CNPJ (V4019)
- Auxílio de moradores do domicílio (V4015)
- Presença de Sócios (V4017)
