# 02_harmonization.R
# Harmonização e Criação de Variáveis Derivadas (FOCO: ECONOMIA SOLIDÁRIA E RURAL)

source("scripts_r/00_setup.R")

# 1. FUNÇÃO DE HARMONIZAÇÃO POR ANO ------------------------------------------
harmonize_pnadc <- function(df) {
  # Limpeza de Tipos e Forçar Numérico para Pesos (Crítico para Survey)
  df <- df %>% 
    mutate(across(everything(), as.character)) %>% 
    mutate(across(c(Ano, Trimestre, V2009, V1028, starts_with("V1028")), suppressWarnings(as.numeric)))

  if (!("Habitual" %in% names(df))) df$Habitual <- 1.0

  df_transformed <- df %>%
    mutate(
      V2009 = as.numeric(V2009),
      # --- BLOCO A: MERCADO DE TRABALHO GERAL ---
      pia = ifelse(V2009 >= 14, 1, 0),
      ocupado = ifelse(VD4002 == "1", 1, 0),
      desocupado = ifelse(VD4002 == "2", 1, 0),
      forca_trabalho = ifelse(VD4001 == "1", 1, 0),
      subutilizado = ifelse(VD4002 == "2" | VD4004A == "1" | VD4003 == "1", 1, 0),
      informal = case_when(
        V4012 == "3" & V4029 == "2" ~ 1,
        V4012 == "1" & V4029 == "2" ~ 1,
        V4012 == "5" & V4019 == "2" ~ 1,
        V4012 == "6" & V4019 == "2" ~ 1,
        V4012 == "7" ~ 1,
        ocupado == 1 ~ 0,
        TRUE ~ NA_real_
      ),
      contribuidor_prev = ifelse(VD4012 == "1", 1, 0),
      agropecuaria = ifelse(VD4010 == "01", 1, 0), # Ajustado para código "01"
      rural = ifelse(V1022 == "2", 1, 0),
      Rend_H_real = as.numeric(gsub(",", ".", VD4016)) * as.numeric(Habitual),
      
      # --- BLOCO B: PROXIES DE ECONOMIA SOLIDÁRIA (FOCO) ---
      # Unidade que possui sócios ou ajuda de familiares (Proxy Cooperativismo/Coletivismo)
      ees_proxy_coletivo = ifelse(V4017 == "1" | V4015 == "1" | (suppressWarnings(as.numeric(V4018)) >= 2 & suppressWarnings(as.numeric(V4018)) <= 5), 1, 0),
      
      negocio_sem_cnpj = ifelse(V4019 == "2", 1, 0),
      ees_coletivo_informal = ifelse(ees_proxy_coletivo == 1 & negocio_sem_cnpj == 1, 1, 0),
      
      # Tipologia de Empreendimento
      ees_tipo_unidade = case_when(
        V4017 == "1" ~ "Societário/Cooperativo",
        V4015 == "1" & V4016 == "2" ~ "Unidade Familiar",
        V4016 == "2" & V4017 == "2" & V4015 == "2" ~ "Individual/Autônomo",
        TRUE ~ "Outros"
      ),
      
      # --- BLOCO C: TRABALHO FAMILIAR E RURAL ---
      trabalhador_familiar_auxiliar = ifelse(VD4009 == "10", 1, 0),
      tf_auxiliar_rural = ifelse(trabalhador_familiar_auxiliar == 1 & rural == 1, 1, 0),
      
      # --- BLOCO D: VULNERABILIDADE ---
      agro_rural_vulneravel = ifelse(agropecuaria == 1 & rural == 1 & (informal == 1 | contribuidor_prev == 2), 1, 0),
      baixo_rendimento_rural = ifelse(rural == 1 & Rend_H_real < 1412, 1, 0), # 1 SM 2024 proxy
      
      # --- CATEGORIAS SOCIAIS ---
      sexo = factor(V2007, levels = c("1", "2"), labels = c("Homem", "Mulher")),
      raca = case_when(
        V2010 == "1" ~ "Branco",
        V2010 == "2" ~ "Preto",
        V2010 %in% c("3","4","5") ~ "Pardo/Preto/Outros",
        TRUE ~ "Não declarado"
      )
    )
  
  return(df_transformed)
}

# 2. PROCESSAMENTO SEQUENCIAL ------------------------------------------------
silver_dir <- "data/silver/pnadc"
gold_dir <- "data/gold/pnadc"
dir.create(gold_dir, recursive = TRUE, showWarnings = FALSE)

arquivos <- sort(list.files(silver_dir, pattern = "*.parquet", full.names = TRUE))

for (arq in arquivos) {
  ano <- str_extract(basename(arq), "\\d{4}")
  log_status(paste("Harmonizando (RAW Codes) Ano:", ano))
  
  df_ano <- read_parquet(arq)
  df_ano_harm <- harmonize_pnadc(df_ano)
  
  write_parquet(df_ano_harm, file.path(gold_dir, paste0("pnadc_gold_", ano, ".parquet")))
  log_status(paste("Sucesso Camada Gold:", ano))
  
  rm(df_ano, df_ano_harm); gc()
}

message("Harmonização focada em Economia Solidária finalizada.")
