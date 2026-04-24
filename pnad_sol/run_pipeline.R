# run_pipeline.R
# Script Mestre: Pipeline PNAD SOL (Trabalho e Renda RN)

# 1. Setup Ambiental e Log
source("scripts_r/00_setup.R")

log_status("--- INICIANDO PIPELINE PNAD SOL (RURAL RN) ---")

# 2. Ingestão e Parquetização (Baixa em ../download_pnad -> Salva em data/silver)
log_status("Fase 1/3: Ingestão de Microdados...")
source("scripts_r/01_ingestion.R")

# 3. Harmonização (data/silver -> data/gold)
log_status("Fase 2/3: Harmonização e Variaveis Derivadas...")
source("scripts_r/02_harmonization.R")

# 4. Análise e Consolidação (data/gold -> data/results)
log_status("Fase 3/3: Análise Amostral e Exportação...")
source("scripts_r/03_analysis_survey.R")

# 5. Auditoria de Representatividade
log_status("Gerando Relatório de Saúde da Amostra (n real)...")
source("scripts_r/report_sample_health.R")

log_status("--- PIPELINE PNAD SOL CONCLUÍDO COM SUCESSO ---")
log_status("Resultados finais disponíveis em pnad_sol/data/results/")
