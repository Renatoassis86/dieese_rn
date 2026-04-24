# validation_comparativo.R
# Tabela Comparativa Estendida: Ocupação e Rendimento (RN)

source("scripts_r/00_setup.R")

# 1. BENCHMARKS (Dados extraídos de T1 e T5)
benchmarks <- data.frame(
  ano = c(2019, 2020, 2021, 2022, 2023, 2024),
  ocup_ref = c(1283.1, 1220.7, 1280.1, 1319.3, 1314.7, 1388.8),
  inf_ref  = c(616.8, 560.3, 578.0, 591.4, 556.8, 590.5),
  renda_f_ref = c(3717, 3245, 3026, 3112, 3296, 3199), # Renda Média Formal
  renda_i_ref = c(1175, 1205, 1145, 1263, 1265, 1591)  # Renda Média Informal
)

results_list <- list()

for (i in 1:nrow(benchmarks)) {
  ano_target <- benchmarks$ano[i]
  gold_file <- file.path("data/gold/pnadc", paste0("pnadc_gold_", ano_target, ".parquet"))
  
  if (!file.exists(gold_file)) next
  
  log_status(paste("Validando Ocupação e Renda para:", ano_target))
  
  df <- read_parquet(gold_file)
  rep_weights_cols <- grep("^V1028[0-9]+", names(df), value = TRUE)
  
  des <- survey::svrepdesign(
    data = df, weights = ~V1028, type = "bootstrap",
    repweights = "^V1028[0-9]+", 
    combined.weights = TRUE,
    mse = TRUE,
    replicates = length(rep_weights_cols),
    df = length(rep_weights_cols)
  ) %>% srvyr::as_survey_rep()
  
  calc <- des %>%
    filter(UF == "24") %>%
    summarise(
      ocup_calc = survey_total(ocupado == 1, na.rm = TRUE) / 1000,
      inf_calc  = survey_total(informal == 1, na.rm = TRUE) / 1000,
      renda_f_calc = survey_mean(Rend_H_real, na.rm = TRUE, subset = (informal == 0 & ocupado == 1 & Rend_H_real > 0)),
      renda_i_calc = survey_mean(Rend_H_real, na.rm = TRUE, subset = (informal == 1 & ocupado == 1 & Rend_H_real > 0))
    )
  
  results_list[[as.character(ano_target)]] <- data.frame(
    ano = ano_target,
    ocup_ref = benchmarks$ocup_ref[i],
    ocup_calc = round(calc$ocup_calc, 1),
    inf_ref = benchmarks$inf_ref[i],
    inf_calc = round(calc$inf_calc, 1),
    renda_f_ref = benchmarks$renda_f_ref[i],
    renda_f_calc = round(calc$renda_f_calc, 0),
    renda_i_ref = benchmarks$renda_i_ref[i],
    renda_i_calc = round(calc$renda_i_calc, 0)
  )
}

if (length(results_list) > 0) {
  tabela_final <- bind_rows(results_list) %>%
    mutate(
      status_vaga = ifelse(abs(ocup_calc - ocup_ref) < 1, "✅", "❌"),
      status_renda = ifelse(abs(renda_f_calc - renda_f_ref) < 50, "✅", "⚠️")
    )
  
  write_csv(tabela_final, "data/results/validacao_comparativa_completa.csv")
  cat("\n--- TABELA COMPARATIVA (OCUPAÇÃO E RENDA RN) ---\n")
  print(tabela_final)
} else {
  cat("\nAguardando processamento da Fase Gold para anos do benchmark (2019+).\n")
}
