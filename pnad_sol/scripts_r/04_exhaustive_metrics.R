# 04_exhaustive_metrics.R
# Geração de Indicadores Exaustivos (Gênero, Juventude e Educação) para o RN Rural

source("scripts_r/00_setup.R")
library(survey)

gold_dir <- "data/gold/pnadc"
results_dir <- "data/results"
dir.create(results_dir, recursive = TRUE, showWarnings = FALSE)

# 1. CARREGAR DADO MAIS RECENTE (2024 ou 2023)
arquivos <- list.files(gold_dir, pattern = "*.parquet", full.names = TRUE)
ultimo_arq <- tail(sort(arquivos), 1)
df <- read_parquet(ultimo_arq)

# 2. DEFINIÇÃO DO DESENHO AMOSTRAL
options(survey.lonely.psu = "adjust")
design <- svydesign(ids = ~V1008, strata = ~V1014, weights = ~V1028, data = df, nest = TRUE)
design_rural <- subset(design, rural == 1 & ocupado == 1)

# 3. CÁLCULO DE INDICADORES EXAUSTIVOS ----------------------------------------

# A. GÊNERO
ind_genero <- svyby(~Rend_H_real, ~sexo, design_rural, svymean, na.rm = TRUE)
tx_mulheres <- svymean(~I(sexo == "Mulher"), design_rural)

# B. JUVENTUDE E SUCESSÃO (15-29 anos)
df$jovem <- ifelse(df$V2009 >= 15 & df$V2009 <= 29, 1, 0)
tx_jovem <- svymean(~I(V2009 >= 15 & V2009 <= 29), design_rural)

# C. EDUCAÇÃO
# VD3005: Anos de estudo
df$anos_estudo <- as.numeric(df$VD3005)
media_estudo <- svyby(~anos_estudo, ~sexo, design_rural, svymean, na.rm = TRUE)

# D. INDICADORES POR MICRORREGIÃO (A CARNE DO PROJETO)
# Criando um subset para o RN
design_rn <- subset(design, rural == 1)

final_metrics <- svyby(
  ~interaction(informal, subutilizado, tf_auxiliar_rural, agro_rural_vulneravel, Rend_H_real),
  ~V1023, # Microrregião / Capital vs Interior (Na PNADC V1023 ou similar)
  design_rn, 
  svymean, na.rm=TRUE
)

# Exportando para o Integrador Python
# Criamos um resumão para o Python ler e distribuir pelos municípios
resumo_final <- df %>%
  filter(rural == 1) %>%
  group_by(V1023) %>% # Usando V1023 como proxy territorial se Microrregião não for clara
  summarise(
    taxa_informalidade = mean(informal, na.rm=TRUE),
    taxa_mulheres_ocupadas = mean(sexo == "Mulher", na.rm=TRUE),
    taxa_jovens_ocupados = mean(V2009 <= 29, na.rm=TRUE),
    renda_media = mean(Rend_H_real, na.rm=TRUE),
    escolaridade_media = mean(as.numeric(VD3005), na.rm=TRUE),
    tx_vulnerabilidade_agro = mean(agro_rural_vulneravel, na.rm=TRUE),
    tx_trabalho_familia = mean(tf_auxiliar_rural, na.rm=TRUE)
  )

write_csv(resumo_final, file.path(results_dir, "pnad_rural_rn_deep_metrics.csv"))
log_status("Métricas Exaustivas (Gênero/Juventude/Educação) salvas com sucesso.")
