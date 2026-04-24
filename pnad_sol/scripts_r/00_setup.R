# 00_setup.R
# Script de configuração de ambiente para o Projeto PNAD SOL (RN)

# 0. Configuração de Biblioteca Local e Log
local_lib <- file.path(getwd(), "r_libs")
log_file <- file.path(getwd(), "status_pipeline.txt")

log_status <- function(msg) {
  timestamp <- format(Sys.time(), "[%Y-%m-%d %H:%M:%S]")
  full_msg <- paste(timestamp, msg)
  message(full_msg)
  write(full_msg, file = log_file, append = TRUE)
}

if (!dir.exists(local_lib)) dir.create(local_lib, recursive = TRUE)
.libPaths(c(local_lib, .libPaths()))

# 1. Instalação e Carregamento de pacotes (Granular para evitar falhas no meta-pacote tidyverse)
required_packages <- c(
  "dplyr", "tidyr", "readr", "purrr", "stringr", "magrittr", 
  "PNADcIBGE", "survey", "srvyr", "arrow", "bit64", "tzdb"
)

load_or_install <- function(package) {
  if (!require(package, character.only = TRUE)) {
    message(paste("Tentando instalar", package, "..."))
    tryCatch({
      install.packages(package, lib = local_lib, dependencies = TRUE, repos = "https://cloud.r-project.org")
      library(package, lib.loc = local_lib, character.only = TRUE)
    }, error = function(e) {
      # Tenta sem o argumento lib se falhar (pode ser que o usuário tenha instalado no global entre turnos)
      tryCatch({
        install.packages(package, dependencies = TRUE, repos = "https://cloud.r-project.org")
        library(package, character.only = TRUE)
      }, error = function(e2) {
         warning(paste("Falha ao carregar/instalar", package, ". O pipeline pode falhar."))
      })
    })
  }
}

message("Verificando dependências...")
for (pkg in required_packages) {
  load_or_install(pkg)
}

# 2. Configurações Globais (Conforme estudo_informalidade)
options(survey.lonely.psu = "adjust")
options(timeout = 3600)

library(dplyr)
library(tidyr)
library(readr)
library(purrr)
library(stringr)
library(magrittr)
library(PNADcIBGE)
library(survey)
library(srvyr)
library(arrow)

message("Ambiente R configurado com sucesso para o projeto PNAD SOL.")
