# validation_survey.R
# Teste de Ponderação Amostral: Comparação com estudo_informalidade_2025

source("scripts_r/00_setup.R")

# Parâmetros de Teste
ano_teste <- 2023
gold_file <- file.path("data/gold/pnadc", paste0("pnadc_gold_", ano_teste, ".parquet"))

# Benchmark (T1_informalidade_total.csv)
benchmark <- data.frame(
  ano = 2023,
  local = "Rio Grande do Norte",
  ocupados_ref = 1314.7,  # em milhares
  informais_ref = 556.8,
  tx_informal_ref = 42.3
)

if (!file.exists(gold_file)) {
  stop(paste("Arquivo gold para", ano_teste, "ainda não foi gerado."))
}

df <- read_parquet(gold_file)

# Criando Desenho Amostral
log_status(paste("Validando ponderação para RN no ano", ano_teste))
rep_weights_cols <- grep("^V1028[0-9]+", names(df), value = TRUE)

des <- survey::svrepdesign(
  data = df, weights = ~V1028, type = "bootstrap",
  repweights = "^V1028[0-9]+", mse = TRUE,
  replicates = length(rep_weights_cols),
  df = length(rep_weights_cols)
) %>% srvyr::as_survey_rep()

# Cálculo RN
validacao <- des %>%
  filter(UF == "Rio Grande do Norte") %>%
  summarise(
    ocupados_k = survey_total(ocupado == 1, na.rm = TRUE) / 1000,
    informais_k = survey_total(informal == 1, na.rm = TRUE) / 1000,
    tx_informalidade = survey_mean(informal == 1, na.rm = TRUE) * 100
  )

# Comparação
cat("\n--- RESULTADO DA VALIDAÇÃO (RN 4º TRI 2023) ---\n")
cat(paste("Ocupados (K):  ", round(validacao$ocupados_k, 1), " (Ref: ", benchmark$ocupados_ref, ")\n"))
cat(paste("Informais (K): ", round(validacao$informais_k, 1), " (Ref: ", benchmark$informais_ref, ")\n"))
cat(paste("Taxa Inf (%):  ", round(validacao$tx_informalidade, 1), " (Ref: ", benchmark$tx_informal_ref, ")\n"))

# --- PAINEL DE REPRESENTATIVIDADE (IBGE/IPEA/DIEESE) ---
saude_amostra <- df %>%
  filter(UF == "Rio Grande do Norte") %>%
  group_by(rural) %>%
  summarise(
    n_real = n(),
    n_expandido = sum(V1028, na.rm = TRUE)
  )

cat("\n--- PAINEL DE SAÚDE DA AMOSTRA (REPRESENTATIVIDADE) ---\n")
print(saude_amostra)
cat("\nNota: Se n_real < 30, o dado é considerado instável pelo critério IPEA/IBGE.\n")
