# 01_ingestion.R
# Extração de Microdados PNAD Contínua (4º Trimestre) - 2012 a 2025

source("scripts_r/00_setup.R")

# Parâmetros
anos <- 2012:2025
trimestre <- 4
temp_dir <- "../download_pnad" # Pasta de temporários solicitada
parquet_dir <- "data/silver/pnadc"

dir.create(temp_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(parquet_dir, recursive = TRUE, showWarnings = FALSE)

process_year <- function(ano) {
  parquet_file <- file.path(parquet_dir, paste0("pnadc_", ano, "_q4.parquet"))
  
  if (file.exists(parquet_file)) {
    log_status(paste("Pulando ano", ano, "- Parquet já existe."))
    return(NULL)
  }
  
  log_status(paste("Iniciando download PNAD Contínua:", ano, "Q4 em", temp_dir))
  
  tryCatch({
    # Download e leitura básica
    data_raw <- get_pnadc(
      year = ano, 
      quarter = trimestre, 
      vars = c("Ano","Trimestre","UF","Estrato","UPA","V1028","V2007","V2009","V2010","VD3004",
               "VD4001","VD4002","VD4003","VD4004A","VD4005","V4010","VD4009","V4012","V4015",
               "V4016","V4017","V4018","V4019","V4029","VD4010","VD4011","VD4012","VD4016",
               "VD4031","VD4035","Habitual","V1022","V40332","V40502","V40333","V40503"), 
      labels = FALSE,
      design = FALSE,
      savedir = temp_dir
    )
    
    # Salvar em Parquet
    write_parquet(data_raw, parquet_file)
    log_status(paste("Ano", ano, "convertido para Parquet em:", parquet_file))
    
    # Limpeza de memória
    rm(data_raw)
    gc()
    
  }, error = function(e) {
    message(paste("Erro no ano", ano, ":", e$message))
  })
}

# Execução do loop
walk(anos, process_year)

message("Fase de Ingestão e Conversão Concluída.")
