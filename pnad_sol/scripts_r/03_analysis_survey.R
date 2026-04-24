# 03_analysis_survey.R
# Análise Amostral e Geração de Indicadores Consolidados
# Baseado na lógica de variância de estudo_informalidade_2025/estudo_informalidade_2025_oficial_validado_ibge.R

source("scripts_r/00_setup.R")

# Ajuste global para PSUs isoladas (Conforme linha 19 do ref)
options(survey.lonely.psu = "adjust")

gold_dir <- "data/gold/pnadc"
result_dir <- "data/results"
dir.create(result_dir, recursive = TRUE, showWarnings = FALSE)

# 1. FUNÇÃO DE CÁLCULO POR ANO -----------------------------------------------
analyze_year <- function(ano) {
  arq <- file.path(gold_dir, paste0("pnadc_gold_", ano, ".parquet"))
  if (!file.exists(arq)) return(NULL)
  
  df <- read_parquet(arq)
  
  # Criando Design Amostral de Pesos Replicados (Bootstrap - IBGE/DIEESE)
  log_status(paste("Criando desenho amostral para o ano", ano, "..."))
  
  # Identificando colunas de pesos replicados presentes
  rep_weights_cols <- grep("^V1028[0-9]+", names(df), value = TRUE)
  
  des_raw <- survey::svrepdesign(
    data = df, 
    weights = ~V1028, 
    type = "bootstrap",
    repweights = "^V1028[0-9]+", 
    combined.weights = TRUE, # Obrigatório para pesos replicados do IBGE
    mse = TRUE,
    replicates = length(rep_weights_cols),
    df = length(rep_weights_cols)
  )
  
  des <- srvyr::as_survey_rep(des_raw)
  
  log_status(paste("Calculando estimativas para RN e NE no ano", ano, "..."))
  
  # Análise Agregada RN
  res_rn <- des %>%
    filter(UF == "24") %>%
    summarise(
      # Mercados e Informalidade (Base Validada)
      taxa_desocupacao = survey_mean(desocupado == 1, na.rm = TRUE, vartype = "cv"),
      taxa_informalidade = survey_mean(informal == 1, na.rm = TRUE, vartype = "cv"),
      renda_media_real = survey_mean(Rend_H_real, na.rm = TRUE, vartype = "cv"),
      
      # Foco 1: Economia Solidária (Proxies)
      ees_coletivo_informal = survey_mean(ees_coletivo_informal == 1, na.rm = TRUE, vartype = "cv"),
      ees_tipo_societario = survey_mean(ees_tipo_unidade == "Societário/Cooperativo", na.rm = TRUE, vartype = "cv"),
      ees_tipo_familiar = survey_mean(ees_tipo_unidade == "Unidade Familiar", na.rm = TRUE, vartype = "cv"),
      
      # Foco 2: Ruralidade e Vulnerabilidade
      tx_tf_auxiliar_rural = survey_mean(tf_auxiliar_rural == 1, na.rm = TRUE, vartype = "cv"),
      tx_vulnerabilidade_agro = survey_mean(agro_rural_vulneravel == 1, na.rm = TRUE, vartype = "cv"),
      
      # Metadados
      n_amostral = unweighted(n())
    ) %>%
    mutate(ano = ano, local = "Rio Grande do Norte")

  # Análise Nordeste (Comparativo)
  message(paste("Calculando estimativas para Nordeste..."))
  nordeste_ufs <- c("21","22","23","24","25","26","27","28","29")
  
  res_ne <- des %>%
    filter(UF %in% nordeste_ufs) %>%
    summarise(
      taxa_desocupacao = survey_mean(desocupado == 1, na.rm = TRUE, vartype = "cv"),
      taxa_informalidade = survey_mean(informal == 1, na.rm = TRUE, vartype = "cv"),
      renda_media_real = survey_mean(Rend_H_real, na.rm = TRUE, vartype = "cv"),
      n_amostral = unweighted(n())
    ) %>%
    mutate(ano = ano, local = "Nordeste")

  return(bind_rows(res_rn, res_ne))
}

# 2. ITERAÇÃO LONGITUDINAL ----------------------------------------------------
anos <- 2012:2024
resultados_list <- map(anos, analyze_year)
indicadores_brutos <- bind_rows(resultados_list)

# 3. CLASSIFICAÇÃO DE QUALIDADE (CV) -------------------------------------------
indicadores_finais <- indicadores_brutos %>%
  mutate(across(ends_with("_cv"), ~case_when(
    . <= 0.15 ~ "Robusto",
    . <= 0.30 ~ "Cautela",
    TRUE ~ "Suprimir"
  ), .names = "qualidade_{.col}"))

# 4. EXPORTAÇÃO ---------------------------------------------------------------
write_csv(indicadores_finais, file.path(result_dir, "pnad_sol_indicadores_consolidados.csv"))

message("Análise finalizada. Resultados em pnad_sol/data/results/pnad_sol_indicadores_consolidados.csv")
