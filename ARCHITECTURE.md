# Arquitetura do Observatório Rural RN (2024-2026)

Este documento estabelece os padrões técnicos, a infraestrutura de dados e a organização modular do projeto, garantindo transparência, rastreabilidade e escalabilidade conforme os objetivos OE1 a OE5.

## 1. Objetivos do Estudo
- **OE1**: Base temática única e integrada.
- **OE2**: Recortes territoriais (Município como chave mínima).
- **OE3**: Indicadores e Tipologias.
- **OE4**: Produtos Visuais (Infográficos, Mapas).
- **OE5**: Governança e Transparência (Nota Metodológica).

## 2. Matriz de Dados (6 Dimensões)
1. **Economia Solidária**: CADSOL e registros estaduais.
2. **Mercado Institucional**: PAA (MiSocial/PAA-Leite) e PNAE.
3. **Estrutura Agropecuária**: Censo Agropecuário IBGE.
4. **Produção e Dinâmica**: PAM, PPM e PEVS (IBGE).
5. **Trabalho e Renda**: PNAD Contínua e RAIS/CAGED.
6. **Vulnerabilidades**: Indicadores Sociais e CadÚnico.

## 3. Pipeline de Dados (Medallion Architecture)
- **Bronze**: Dados brutos extraídos de APIs e planilhas oficiais (`data/bronze/`).
- **Silver**: Dados limpos, tipados e normalizados em formato Parquet (`data/silver/`).
- **Gold**: Dados agregados por indicadores territoriais e séries históricas (`data/gold/`).
- **Supabase**: Persistência final para consumo dinâmico pela plataforma.

## 4. Stack Tecnológica
- **Backend**: Python 3.12 + FastAPI + DuckDB (Processamento local).
- **Database**: Supabase (PostgreSQL + PostgREST).
- **Frontend**: HTML5 + Vanilla CSS + Chart.js (Visualização reativa).
- **Deployment**: Vercel.

## 5. Estrutura de Pastas
- `src/app/`: Frontend (HTML, CSS, JS).
- `src/extraction/`: Scripts de coleta via APIs oficiais.
- `src/transformation/`: Scripts de limpeza e agregação (Medallion).
- `src/integration/`: Sincronização local <-> Supabase.
- `data/`: Armazenamento local temporário (gitignored exceto reference).
- `docs/`: Dicionários de dados e notas metodológicas.
