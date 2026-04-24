# report_sample_health.R
# Auditoria de Representatividade: n real vs n expandido (Foco Rural RN)

source("scripts_r/00_setup.R")

gold_dir <- "data/gold/pnadc"
result_dir <- "data/results"
dir.create(result_dir, recursive = TRUE, showWarnings = FALSE)

arquivos <- list.files(gold_dir, pattern = "*.parquet", full.names = TRUE)

health_list <- list()

for (arq in arquivos) {
  ano <- str_extract(basename(arq), "\\d{4}")
  log_status(paste("Auditando saúde da amostra rural:", ano))
  
  df <- read_parquet(arq)
  
  # Estatística descritiva da amostra para o RN
  stats <- df %>%
    filter(UF == "24") %>%
    group_by(rural) %>%
    summarise(
      n_real = n(),
      n_expandido = sum(V1028, na.rm = TRUE)
    ) %>%
    mutate(
      ano = ano,
      local = ifelse(rural == 1, "RN Rural", "RN Urbano"),
      confiabilidade = case_when(
        n_real >= 100 ~ "Alta",
        n_real >= 30  ~ "Média",
        TRUE          ~ "Baixa/Crítica"
      )
    )
  
  health_list[[ano]] <- stats
}

if (length(health_list) > 0) {
  relatorio_final <- bind_rows(health_list) %>%
    select(ano, local, n_real, n_expandido, confiabilidade) %>%
    arrange(desc(ano), local)
  
  write_csv(relatorio_final, file.path(result_dir, "relatorio_saude_amostra_rn.csv"))
  
  cat("\n--- RELATÓRIO DE SAÚDE DA AMOSTRA (RIO GRANDE DO NORTE) ---\n")
  print(relatorio_final)
  cat("\nRelatório gerado em: pnad_sol/data/results/relatorio_saude_amostra_rn.csv\n")
} else {
  cat("\nNenhum arquivo GOLD encontrado para auditar.\n")
}
