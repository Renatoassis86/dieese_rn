# ============================================================
# PASSO 1 — Setup + Importador ÚNICO (cache, deflator Habitual)
# ============================================================

rm(list = ls()); gc()

suppressPackageStartupMessages({
  library(PNADcIBGE)
  library(dplyr)
  library(srvyr)
  library(survey)
  library(purrr)
  library(readr)
  library(tidyr)
  library(stringr)
})

options(survey.lonely.psu = "adjust")
options(timeout = 600)

# 📂 Diretórios
dir_temp_base <- "D:/pnad_temp"  # cache local
dir_out       <- "D:/repositorio_geral/pnad_continua/estudo_informalidade_2025"
dir.create(dir_temp_base, showWarnings = FALSE, recursive = TRUE)
dir.create(dir_out,       showWarnings = FALSE, recursive = TRUE)

# 🗓️ Trimestres (ajuste à vontade)
trimestres <- list(
  list(tri = 4, ano = 2019),
  list(tri = 4, ano = 2020),
  list(tri = 4, ano = 2021),
  list(tri = 4, ano = 2022),
  list(tri = 4, ano = 2023),
  list(tri = 4, ano = 2024),
  list(tri = 2, ano = 2025)
)

# 🧩 Utilitários
rotulo_tri   <- function(tri, ano) sprintf("%dº tri/%d", tri, ano)
nordeste_ufs <- c(21,22,23,24,25,26,27,28,29)

# Regiões intra-RN (via Estrato)
mapa_regioes_rn <- function(estrato) {
  ce <- trunc(as.numeric(estrato) / 1000)
  dplyr::case_when(
    ce == 2410 ~ "Natal(RN)",
    ce == 2420 ~ "Entorno metropolitano de Natal(RN)",
    ce == 2451 ~ "Agreste do RN",
    ce == 2452 ~ "Oeste do RN",
    ce == 2453 ~ "Central do RN",
    TRUE ~ NA_character_
  )
}

# Rótulos VD4010 (setor) e VD4009 (posição)
rotulos_vd4010 <- c(
  "1"="Agricultura, pecuária, produção florestal, pesca e aquicultura",
  "2"="Indústria geral",
  "3"="Construção",
  "4"="Comércio, reparação de veículos automotores e motocicletas",
  "5"="Transporte, armazenagem e correio",
  "6"="Alojamento e alimentação",
  "7"="Informação, comunicação e atividades financeiras, imobiliárias, profissionais e administrativas",
  "8"="Administração pública, defesa e seguridade social",
  "9"="Educação, saúde humana e serviços sociais",
  "10"="Outros Serviços",
  "11"="Serviços domésticos",
  "12"="Atividades mal definidas"
)
rotulos_vd4009 <- c(
  "1" ="Empregado privado com carteira",
  "2" ="Empregado privado sem carteira",
  "3" ="Doméstico com carteira",
  "4" ="Doméstico sem carteira",
  "5" ="Empregado setor público com carteira",
  "6" ="Empregado setor público sem carteira",
  "7" ="Militar/estatutário",
  "8" ="Empregador",
  "9" ="Conta-própria",
  "10"="Trabalhador familiar auxiliar"
)

lbl_sexo <- function(v) ifelse(v == 1, "Homem", "Mulher")
faixa_idade <- function(idade) case_when(
  idade >= 14 & idade <= 24 ~ "14–24",
  idade >= 25 & idade <= 39 ~ "25–39",
  idade >= 40 & idade <= 59 ~ "40–59",
  idade >= 60               ~ "60+",
  TRUE ~ NA_character_
)
lbl_raca <- function(v) case_when(
  v == 1 ~ "Branco",
  v == 2 ~ "Preto",
  v %in% c(3,4,5) ~ "Demais Raças",
  TRUE ~ NA_character_
)
lbl_escolar <- function(vd3004) case_when(
  vd3004 %in% c(1,2)   ~ "Fundamental ou menos",
  vd3004 %in% c(3,4)   ~ "Médio",
  vd3004 %in% c(5,6,7) ~ "Superior",
  TRUE ~ NA_character_
)

# Desenhos amostrais
faz_desenho_amostral_rep <- function(df){
  des <- survey::svrepdesign(
    data = df,
    weights = ~V1028,
    type = "bootstrap",
    repweights = "V1028[0-9]+",
    mse = TRUE,
    replicates = length(sprintf("V1028%03d", 1:200)),
    df = length(sprintf("V1028%03d", 1:200))
  )
  srvyr::as_survey_rep(des)
}
faz_desenho_amostral_classic <- function(df){
  df %>% srvyr::as_survey_design(ids = UPA, strata = Estrato, weights = V1028, nest = TRUE)
}

# Importador ÚNICO (baixa 1x/tri e reusa; deflaciona via Habitual)
importa_pnad_design <- function(tri, ano, method = c("classic","rep")){
  method <- match.arg(method)
  vars <- c(
    "Ano","Trimestre","UF","Estrato","UPA","V1028",
    "V2007","V2009","V2010","VD3004",
    "VD4001","VD4002","VD4003","VD4004A","VD4005",
    "V4010","VD4009","V4012","V4019","V4029","VD4012",
    "VD4016","VD4031","VD4035","Habitual"
  )
  
  savedir <- file.path(dir_temp_base, sprintf("PNADC_%02d%d", tri, ano))
  if (!dir.exists(savedir)) dir.create(savedir, recursive = TRUE, showWarnings = FALSE)
  
  df <- PNADcIBGE::get_pnadc(
    year    = ano, quarter = tri,
    vars    = vars,
    labels  = FALSE, design = FALSE,
    savedir = savedir
  )
  
  # Se 'Habitual' não veio na base, mantém 1.0 como fallback
  if (!("Habitual" %in% names(df))) df$Habitual <- 1.0
  
  # Coagir numérico
  to_num <- intersect(vars, names(df))
  df <- df %>% mutate(across(all_of(to_num), suppressWarnings(as.numeric)))
  
  df <- df %>%
    mutate(
      regioes_rn  = mapa_regioes_rn(Estrato),
      Rend_H_real = VD4016 * Habitual,
      setor_lbl   = dplyr::recode(as.character(V4010), !!!rotulos_vd4010, .default = NA_character_),
      pos_ocup    = dplyr::recode(as.character(VD4009), !!!rotulos_vd4009, .default = NA_character_)
    )
  
  if (method == "rep") {
    faz_desenho_amostral_rep(df)
  } else {
    c_drop <- intersect(names(df), sprintf("V1028%03d", 1:200))
    if (length(c_drop)) df <- dplyr::select(df, -dplyr::all_of(c_drop))
    faz_desenho_amostral_classic(df)
  }
}

# 🧠 Regra de informalidade
cria_informal <- function(dsg){
  dsg %>% mutate(informal = dplyr::case_when(
    V4012 == 3 & V4029 == 2 ~ 1,  # empregado privado sem carteira
    V4012 == 1 & V4029 == 2 ~ 1,  # doméstico sem carteira
    V4012 == 5 & V4019 == 2 ~ 1,  # empregador sem CNPJ
    V4012 == 6 & V4019 == 2 ~ 1,  # conta-própria sem CNPJ
    V4012 == 7              ~ 1,  # trabalhador familiar auxiliar
    TRUE ~ 0
  ))
}



# ============================================================
# PASSO 2 — TODAS as funções de métricas (sem novos downloads)
# ============================================================

# A) Mercado de trabalho básico
calc_mercado_basico <- function(dsg, tri, ano){
  dsg %>% summarise(
    PIA  = survey_total(V2009 >= 14, na.rm=TRUE),
    PEA  = survey_total(VD4001 == 1, na.rm=TRUE),
    Ocup = survey_total(VD4002 == 1, na.rm=TRUE),
    Deso = survey_total(VD4002 == 2, na.rm=TRUE)
  ) %>% transmute(trimestre=rotulo_tri(tri,ano),
                  PIA_k=round(PIA/1000,1), PEA_k=round(PEA/1000,1),
                  Ocup_k=round(Ocup/1000,1), Deso_k=round(Deso/1000,1),
                  tx_part=round(100*PEA/pmax(PIA,1),1),
                  tx_desoc=round(100*Deso/pmax(PEA,1),1))
}

# B) Informalidade total — BR/NE/RN
calc_inf_total_locais <- function(dsg, tri, ano){
  monta <- function(subd, local){
    subd %>% filter(VD4002==1) %>% cria_informal() %>%
      summarise(ocup=survey_total(na.rm=TRUE), inf=survey_total(informal,na.rm=TRUE)) %>%
      transmute(trimestre=rotulo_tri(tri,ano), local=local,
                ocupados_k=round(ocup/1000,1), informais_k=round(inf/1000,1),
                formais_k=round((ocup-inf)/1000,1),
                tx_informalidade=round(100*inf/pmax(ocup,1),1))
  }
  dplyr::bind_rows(
    monta(dsg, "Brasil"),
    monta(dsg %>% dplyr::filter(UF %in% nordeste_ufs), "Nordeste"),
    monta(dsg %>% dplyr::filter(UF == 24),             "Rio Grande do Norte")
  )
}

# C) Informalidade por grupos (sexo, faixa etária, raça/cor, escolaridade)
calc_inf_por_grupo <- function(dsg, tri, ano, var=c("sexo","idade","raca","escolar")){
  var <- match.arg(var)
  add_group <- switch(var,
                      sexo    = \(x) mutate(x, grupo = lbl_sexo(V2007)),
                      idade   = \(x) mutate(x, grupo = faixa_idade(V2009)),
                      raca    = \(x) mutate(x, grupo = lbl_raca(V2010)),
                      escolar = \(x) mutate(x, grupo = lbl_escolar(VD3004))
  )
  lab <- switch(var, sexo="Sexo", idade="FaixaEtaria", raca="Raca", escolar="Escolaridade")
  monta <- function(subd, local){
    subd %>% filter(VD4002==1) %>% cria_informal() %>%
      add_group() %>% filter(!is.na(grupo)) %>%
      group_by(grupo) %>%
      summarise(ocup=survey_total(na.rm=TRUE), inf=survey_total(informal,na.rm=TRUE), .groups="drop") %>%
      transmute(trimestre=rotulo_tri(tri,ano), local=local, !!lab := grupo,
                ocupados_k=round(ocup/1000,1), informais_k=round(inf/1000,1),
                formais_k=round((ocup-inf)/1000,1),
                tx_informalidade=round(100*inf/pmax(ocup,1),1))
  }
  dplyr::bind_rows(
    monta(dsg, "Brasil"),
    monta(dsg %>% dplyr::filter(UF %in% nordeste_ufs), "Nordeste"),
    monta(dsg %>% dplyr::filter(UF == 24),             "Rio Grande do Norte")
  )
}

# D) Informalidade por setor (VD4010) — nível e taxa
calc_inf_por_setor <- function(dsg, tri, ano){
  monta <- function(subd, local){
    subd %>% filter(VD4002==1) %>% cria_informal() %>%
      mutate(setor = ifelse(is.na(setor_lbl), as.character(V4010), setor_lbl)) %>%
      group_by(setor) %>%
      summarise(ocup=survey_total(na.rm=TRUE), inf=survey_total(informal,na.rm=TRUE), .groups="drop") %>%
      transmute(trimestre=rotulo_tri(tri,ano), local=local, setor=setor,
                ocupados_k=round(ocup/1000,1), informais_k=round(inf/1000,1),
                tx_informalidade=round(100*inf/pmax(ocup,1),1))
  }
  dplyr::bind_rows(
    monta(dsg, "Brasil"),
    monta(dsg %>% dplyr::filter(UF %in% nordeste_ufs), "Nordeste"),
    monta(dsg %>% dplyr::filter(UF == 24),             "Rio Grande do Norte")
  )
}

# E) Distribuição dos informais por setor (participações)
calc_mix_setorial_informais <- function(dsg, tri, ano){
  monta <- function(subd, local){
    subd %>% filter(VD4002==1) %>% cria_informal() %>%
      mutate(setor = ifelse(is.na(setor_lbl), as.character(V4010), setor_lbl)) %>%
      group_by(setor) %>%
      summarise(inf=survey_total(informal,na.rm=TRUE), .groups="drop_last") %>%
      mutate(total_inf=sum(inf,na.rm=TRUE), part_pct=round(100*inf/pmax(total_inf,1),1)) %>%
      transmute(trimestre=rotulo_tri(tri,ano), local=local, setor=setor,
                informais_k=round(inf/1000,1), part_informais=part_pct)
  }
  dplyr::bind_rows(
    monta(dsg, "Brasil"),
    monta(dsg %>% dplyr::filter(UF %in% nordeste_ufs), "Nordeste"),
    monta(dsg %>% dplyr::filter(UF == 24),             "Rio Grande do Norte")
  )
}

# F) Informalidade — Regiões do RN
calc_inf_regioesRN <- function(dsg, tri, ano){
  dsg %>% filter(UF==24, !is.na(regioes_rn), VD4002==1) %>% cria_informal() %>%
    group_by(regioes_rn) %>%
    summarise(ocup=survey_total(na.rm=TRUE), inf=survey_total(informal,na.rm=TRUE), .groups="drop") %>%
    transmute(trimestre=rotulo_tri(tri,ano), local=regioes_rn,
              ocupados_k=round(ocup/1000,1), informais_k=round(inf/1000,1),
              formais_k=round((ocup-inf)/1000,1),
              tx_informalidade=round(100*inf/pmax(ocup,1),1))
}

# G) Subocupação (nível e taxa)
calc_subocupacao <- function(dsg, tri, ano){
  monta <- function(subd, local){
    subd %>% summarise(PEA=survey_total(VD4001==1,na.rm=TRUE),
                       subocup=survey_total(VD4004A==1,na.rm=TRUE)) %>%
      transmute(trimestre=rotulo_tri(tri,ano), local=local,
                subocup_k=round(subocup/1000,1), PEA_k=round(PEA/1000,1),
                tx_subocup=round(100*subocup/pmax(PEA,1),1))
  }
  dplyr::bind_rows(
    monta(dsg,"Brasil"),
    monta(dsg %>% dplyr::filter(UF %in% nordeste_ufs),"Nordeste"),
    monta(dsg %>% dplyr::filter(UF==24),"Rio Grande do Norte")
  )
}

# H) Fora da força de trabalho (FTP e desalento)
calc_ftp_desalento <- function(dsg, tri, ano){
  monta <- function(subd, local){
    subd %>% summarise(foraFT=survey_total(VD4001==2,na.rm=TRUE),
                       FTP=survey_total(VD4003==1,na.rm=TRUE),
                       desal=survey_total(VD4005==1,na.rm=TRUE)) %>%
      transmute(trimestre=rotulo_tri(tri,ano), local=local,
                FTP_k=round(FTP/1000,1), foraFT_k=round(foraFT/1000,1),
                desalento_k=round(desal/1000,1),
                part_FTP_em_foraFT=round(100*FTP/pmax(foraFT+FTP,1),1))
  }
  dplyr::bind_rows(
    monta(dsg,"Brasil"),
    monta(dsg %>% dplyr::filter(UF %in% nordeste_ufs),"Nordeste"),
    monta(dsg %>% dplyr::filter(UF==24),"Rio Grande do Norte")
  )
}

# I) Taxa composta de subutilização
calc_tx_composta <- function(dsg, tri, ano){
  monta <- function(subd, local){
    subd %>% summarise(
      desocup=survey_total(VD4002==2,na.rm=TRUE),
      subocup=survey_total(VD4004A==1,na.rm=TRUE),
      FTP    =survey_total(VD4003==1,na.rm=TRUE),
      PEA    =survey_total(VD4001==1,na.rm=TRUE)
    ) %>% transmute(trimestre=rotulo_tri(tri,ano), local=local,
                    numerador_k=round((desocup+subocup+FTP)/1000,1),
                    denominador_k=round((PEA+FTP)/1000,1),
                    tx_composta=round(100*(desocup+subocup+FTP)/pmax(PEA+FTP,1),1))
  }
  dplyr::bind_rows(
    monta(dsg,"Brasil"),
    monta(dsg %>% dplyr::filter(UF %in% nordeste_ufs),"Nordeste"),
    monta(dsg %>% dplyr::filter(UF==24),"Rio Grande do Norte")
  )
}

# J) Previdência (% contribui) — total e por formalidade
calc_previdencia <- function(dsg, tri, ano){
  dsg_inf <- dsg %>% filter(VD4001==1, VD4002==1) %>% cria_informal()
  monta <- function(subd, local, grupo){
    subd %>% summarise(ocup=survey_total(na.rm=TRUE),
                       contrib=survey_total(VD4012==1,na.rm=TRUE)) %>%
      transmute(trimestre=rotulo_tri(tri,ano), local=local, grupo=grupo,
                pct_contrib=round(100*contrib/pmax(ocup,1),1),
                ocup_k=round(ocup/1000,1), contrib_k=round(contrib/1000,1))
  }
  dplyr::bind_rows(
    monta(dsg %>% filter(VD4001==1,VD4002==1), "Brasil","Ocupados - Total"),
    monta(dsg_inf %>% filter(informal==0),     "Brasil","Ocupados - Formais"),
    monta(dsg_inf %>% filter(informal==1),     "Brasil","Ocupados - Informais"),
    monta(dsg %>% filter(UF %in% nordeste_ufs, VD4001==1,VD4002==1), "Nordeste","Ocupados - Total"),
    monta(dsg_inf %>% filter(UF %in% nordeste_ufs, informal==0), "Nordeste","Ocupados - Formais"),
    monta(dsg_inf %>% filter(UF %in% nordeste_ufs, informal==1), "Nordeste","Ocupados - Informais"),
    monta(dsg %>% filter(UF==24, VD4001==1,VD4002==1), "Rio Grande do Norte","Ocupados - Total"),
    monta(dsg_inf %>% filter(UF==24, informal==0), "Rio Grande do Norte","Ocupados - Formais"),
    monta(dsg_inf %>% filter(UF==24, informal==1), "Rio Grande do Norte","Ocupados - Informais")
  )
}

# K) Renda — DEFLACIONADA (Rend_H_real) — média e mediana — Formais vs Informais
calc_renda_formal_informal <- function(dsg, tri, ano){
  dsg_inf <- dsg %>% cria_informal()
  sumariza <- function(subd, local, grp){
    subd %>% filter(VD4001==1, VD4002==1, !is.na(Rend_H_real), Rend_H_real>0) %>%
      summarise(
        media   = survey_mean(Rend_H_real, na.rm=TRUE),
        mediana = survey_median(Rend_H_real, na.rm=TRUE),
        n       = unweighted(n())
      ) %>% transmute(trimestre=rotulo_tri(tri,ano), local=local, grupo=grp,
                      media=round(media,0), mediana=round(mediana,0), n=n)
  }
  dplyr::bind_rows(
    sumariza(dsg_inf %>% filter(informal==0), "Brasil","Formais"),
    sumariza(dsg_inf %>% filter(informal==1), "Brasil","Informais"),
    sumariza(dsg_inf %>% filter(UF %in% nordeste_ufs, informal==0), "Nordeste","Formais"),
    sumariza(dsg_inf %>% filter(UF %in% nordeste_ufs, informal==1), "Nordeste","Informais"),
    sumariza(dsg_inf %>% filter(UF==24, informal==0), "Rio Grande do Norte","Formais"),
    sumariza(dsg_inf %>% filter(UF==24, informal==1), "Rio Grande do Norte","Informais")
  )
}

# L) Horas — habituais/efetivas — Formais vs Informais
calc_horas_formal_informal <- function(dsg, tri, ano){
  dsg_inf <- dsg %>% cria_informal()
  sumariza <- function(subd, local, grp){
    subd %>% filter(VD4001==1, VD4002==1) %>%
      summarise(horas_hab=survey_mean(VD4031,na.rm=TRUE),
                horas_eff=survey_mean(VD4035,na.rm=TRUE)) %>%
      transmute(trimestre=rotulo_tri(tri,ano), local=local, grupo=grp,
                horas_hab=round(horas_hab,1), horas_eff=round(horas_eff,1))
  }
  dplyr::bind_rows(
    sumariza(dsg_inf %>% filter(informal==0), "Brasil","Formais"),
    sumariza(dsg_inf %>% filter(informal==1), "Brasil","Informais"),
    sumariza(dsg_inf %>% filter(UF %in% nordeste_ufs, informal==0), "Nordeste","Formais"),
    sumariza(dsg_inf %>% filter(UF %in% nordeste_ufs, informal==1), "Nordeste","Informais"),
    sumariza(dsg_inf %>% filter(UF==24, informal==0), "Rio Grande do Norte","Formais"),
    sumariza(dsg_inf %>% filter(UF==24, informal==1), "Rio Grande do Norte","Informais")
  )
}

# M) RN — Subocupação, Tx composta e Previdência por região (posest agrupado)
calc_regioesRN_subocup <- function(dsg, tri, ano){
  dsg %>% filter(UF==24, !is.na(regioes_rn)) %>% group_by(regioes_rn) %>%
    summarise(PEA=survey_total(VD4001==1,na.rm=TRUE),
              subocup=survey_total(VD4004A==1,na.rm=TRUE)) %>%
    transmute(trimestre=rotulo_tri(tri,ano), local=regioes_rn,
              subocup_k=round(subocup/1000,1), PEA_k=round(PEA/1000,1),
              tx_subocup=round(100*subocup/pmax(PEA,1),1))
}
calc_regioesRN_txcomp <- function(dsg, tri, ano){
  dsg %>% filter(UF==24, !is.na(regioes_rn)) %>% group_by(regioes_rn) %>%
    summarise(desocup=survey_total(VD4002==2,na.rm=TRUE),
              subocup=survey_total(VD4004A==1,na.rm=TRUE),
              FTP    =survey_total(VD4003==1,na.rm=TRUE),
              PEA    =survey_total(VD4001==1,na.rm=TRUE)) %>%
    transmute(trimestre=rotulo_tri(tri,ano), local=regioes_rn,
              numerador_k=round((desocup+subocup+FTP)/1000,1),
              denominador_k=round((PEA+FTP)/1000,1),
              tx_composta=round(100*(desocup+subocup+FTP)/pmax(PEA+FTP,1),1))
}
calc_regioesRN_previdencia <- function(dsg, tri, ano){
  dsg_inf <- dsg %>% cria_informal()
  total <- dsg %>% filter(UF==24,!is.na(regioes_rn),VD4001==1,VD4002==1) %>%
    group_by(regioes_rn) %>%
    summarise(ocup=survey_total(na.rm=TRUE), contrib=survey_total(VD4012==1,na.rm=TRUE)) %>%
    transmute(trimestre=rotulo_tri(tri,ano), local=regioes_rn, grupo="Ocupados - Total",
              pct_contrib=round(100*contrib/pmax(ocup,1),1),
              ocup_k=round(ocup/1000,1), contrib_k=round(contrib/1000,1))
  form_inf <- dsg_inf %>% filter(UF==24,!is.na(regioes_rn),VD4001==1,VD4002==1) %>%
    mutate(grupo=ifelse(informal==1,"Ocupados - Informais","Ocupados - Formais")) %>%
    group_by(regioes_rn, grupo) %>%
    summarise(ocup=survey_total(na.rm=TRUE), contrib=survey_total(VD4012==1,na.rm=TRUE), .groups="drop") %>%
    transmute(trimestre=rotulo_tri(tri,ano), local=regioes_rn, grupo=grupo,
              pct_contrib=round(100*contrib/pmax(ocup,1),1),
              ocup_k=round(ocup/1000,1), contrib_k=round(contrib/1000,1))
  dplyr::bind_rows(total, form_inf)
}

# N) Gaps RN – Brasil (p.p.) por grupo
calc_gap_RN_BR <- function(dsg, tri, ano, var=c("sexo","idade","raca","escolar")){
  comp <- calc_inf_por_grupo(dsg, tri, ano, var = match.arg(var))
  chave <- setdiff(names(comp), c("trimestre","local","ocupados_k","informais_k","formais_k","tx_informalidade"))[1]
  wide <- comp %>%
    dplyr::select(trimestre, local, !!chave, tx_informalidade) %>%
    tidyr::pivot_wider(names_from = local, values_from = tx_informalidade)
  if(!all(c("Brasil","Rio Grande do Norte") %in% names(wide))) return(tibble())
  wide %>% mutate(gap_pp = `Rio Grande do Norte` - Brasil)
}






#######################################



# ==== A) Mercado de trabalho básico
calc_mercado_basico <- function(dsg, tri, ano){
  dsg %>% summarise(
    PIA  = survey_total(V2009 >= 14, na.rm=TRUE),
    PEA  = survey_total(VD4001 == 1, na.rm=TRUE),
    Ocup = survey_total(VD4002 == 1, na.rm=TRUE),
    Deso = survey_total(VD4002 == 2, na.rm=TRUE)
  ) %>%
    transmute(trimestre=rotulo_tri(tri,ano),
              PIA_k=round(PIA/1000,1), PEA_k=round(PEA/1000,1),
              Ocup_k=round(Ocup/1000,1), Deso_k=round(Deso/1000,1),
              tx_part=round(100*PEA/pmax(PIA,1),1),
              tx_desoc=round(100*Deso/pmax(PEA,1),1),
              def_PIA = "V2009>=14", def_PEA="VD4001==1",
              def_Ocup="VD4002==1", def_Deso="VD4002==2")
}

# ==== B) Informalidade total — BR/NE/RN
calc_inf_total_locais <- function(dsg, tri, ano){
  monta <- function(subd, local){
    subd %>% filter(VD4002==1) %>% cria_informal() %>%
      summarise(ocup=survey_total(na.rm=TRUE),
                inf =survey_total(informal,na.rm=TRUE)) %>%
      transmute(trimestre=rotulo_tri(tri,ano), local=local,
                ocupados_k=round(ocup/1000,1),
                informais_k=round(inf/1000,1),
                formais_k=round((ocup-inf)/1000,1),
                tx_informalidade=round(100*inf/pmax(ocup,1),1),
                def_ocup="VD4002==1", regra_informal="ver cria_informal()")
  }
  dplyr::bind_rows(
    monta(dsg, "Brasil"),
    monta(dsg %>% dplyr::filter(UF %in% nordeste_ufs), "Nordeste"),
    monta(dsg %>% dplyr::filter(UF == 24), "Rio Grande do Norte")
  )
}

# ==== C) Informalidade por grupos (sexo/idade/raça/escolar)
calc_inf_por_grupo <- function(dsg, tri, ano, var=c("sexo","idade","raca","escolar")){
  var <- match.arg(var)
  add_group <- switch(var,
                      sexo    = \(x) mutate(x, grupo = lbl_sexo(V2007)),
                      idade   = \(x) mutate(x, grupo = faixa_idade(V2009)),
                      raca    = \(x) mutate(x, grupo = lbl_raca(V2010)),
                      escolar = \(x) mutate(x, grupo = lbl_escolar(VD3004))
  )
  lab <- switch(var, sexo="Sexo", idade="FaixaEtaria", raca="Raca", escolar="Escolaridade")
  monta <- function(subd, local){
    subd %>% filter(VD4002==1) %>% cria_informal() %>%
      add_group() %>% filter(!is.na(grupo)) %>%
      group_by(grupo) %>%
      summarise(ocup=survey_total(na.rm=TRUE),
                inf =survey_total(informal,na.rm=TRUE), .groups="drop") %>%
      transmute(trimestre=rotulo_tri(tri,ano), local=local, !!lab := grupo,
                ocupados_k=round(ocup/1000,1), informais_k=round(inf/1000,1),
                formais_k=round((ocup-inf)/1000,1),
                tx_informalidade=round(100*inf/pmax(ocup,1),1),
                var_grupo = lab, def_ocup="VD4002==1", regra_informal="ver cria_informal()")
  }
  dplyr::bind_rows(
    monta(dsg, "Brasil"),
    monta(dsg %>% dplyr::filter(UF %in% nordeste_ufs), "Nordeste"),
    monta(dsg %>% dplyr::filter(UF == 24), "Rio Grande do Norte")
  )
}

# ==== D) Informalidade por setor (VD4010)
calc_inf_por_setor <- function(dsg, tri, ano){
  monta <- function(subd, local){
    subd %>% filter(VD4002==1) %>% cria_informal() %>%
      mutate(setor = ifelse(is.na(setor_lbl), as.character(V4010), setor_lbl)) %>%
      group_by(setor) %>%
      summarise(ocup=survey_total(na.rm=TRUE),
                inf =survey_total(informal,na.rm=TRUE), .groups="drop") %>%
      transmute(trimestre=rotulo_tri(tri,ano), local=local, setor=setor,
                ocupados_k=round(ocup/1000,1), informais_k=round(inf/1000,1),
                tx_informalidade=round(100*inf/pmax(ocup,1),1),
                def_setor="V4010 (rotulado)", def_ocup="VD4002==1")
  }
  dplyr::bind_rows(
    monta(dsg, "Brasil"),
    monta(dsg %>% dplyr::filter(UF %in% nordeste_ufs), "Nordeste"),
    monta(dsg %>% dplyr::filter(UF == 24), "Rio Grande do Norte")
  )
}

# ==== E) Mix setorial dos informais (participações)
calc_mix_setorial_informais <- function(dsg, tri, ano){
  monta <- function(subd, local){
    subd %>% filter(VD4002==1) %>% cria_informal() %>%
      mutate(setor = ifelse(is.na(setor_lbl), as.character(V4010), setor_lbl)) %>%
      group_by(setor) %>%
      summarise(inf=survey_total(informal,na.rm=TRUE), .groups="drop_last") %>%
      mutate(total_inf=sum(inf,na.rm=TRUE),
             part_pct=round(100*inf/pmax(total_inf,1),1)) %>%
      transmute(trimestre=rotulo_tri(tri,ano), local=local, setor=setor,
                informais_k=round(inf/1000,1), part_informais=part_pct,
                def_setor="V4010 (rotulado)", regra_informal="ver cria_informal()")
  }
  dplyr::bind_rows(
    monta(dsg, "Brasil"),
    monta(dsg %>% dplyr::filter(UF %in% nordeste_ufs), "Nordeste"),
    monta(dsg %>% dplyr::filter(UF == 24), "Rio Grande do Norte")
  )
}

# ==== F) Informalidade — Regiões do RN
calc_inf_regioesRN <- function(dsg, tri, ano){
  dsg %>% filter(UF==24, !is.na(regioes_rn), VD4002==1) %>% cria_informal() %>%
    group_by(regioes_rn) %>%
    summarise(ocup=survey_total(na.rm=TRUE),
              inf =survey_total(informal,na.rm=TRUE), .groups="drop") %>%
    transmute(trimestre=rotulo_tri(tri,ano), local=regioes_rn,
              ocupados_k=round(ocup/1000,1), informais_k=round(inf/1000,1),
              formais_k=round((ocup-inf)/1000,1),
              tx_informalidade=round(100*inf/pmax(ocup,1),1),
              def_regiao="Estrato→regioes_rn", def_ocup="VD4002==1")
}

# ==== J) Previdência — % contribui
calc_previdencia <- function(dsg, tri, ano){
  dsg_inf <- dsg %>% filter(VD4001==1, VD4002==1) %>% cria_informal()
  monta <- function(subd, local, grupo){
    subd %>% summarise(ocup=survey_total(na.rm=TRUE),
                       contrib=survey_total(VD4012==1,na.rm=TRUE)) %>%
      transmute(trimestre=rotulo_tri(tri,ano), local=local, grupo=grupo,
                pct_contrib=round(100*contrib/pmax(ocup,1),1),
                ocup_k=round(ocup/1000,1), contrib_k=round(contrib/1000,1),
                def_contrib="VD4012==1", def_ocup="VD4001==1 & VD4002==1")
  }
  dplyr::bind_rows(
    monta(dsg %>% filter(VD4001==1,VD4002==1), "Brasil","Ocupados - Total"),
    monta(dsg_inf %>% filter(informal==0),     "Brasil","Ocupados - Formais"),
    monta(dsg_inf %>% filter(informal==1),     "Brasil","Ocupados - Informais"),
    monta(dsg %>% filter(UF %in% nordeste_ufs, VD4001==1,VD4002==1), "Nordeste","Ocupados - Total"),
    monta(dsg_inf %>% filter(UF %in% nordeste_ufs, informal==0), "Nordeste","Ocupados - Formais"),
    monta(dsg_inf %>% filter(UF %in% nordeste_ufs, informal==1), "Nordeste","Ocupados - Informais"),
    monta(dsg %>% filter(UF==24, VD4001==1,VD4002==1), "Rio Grande do Norte","Ocupados - Total"),
    monta(dsg_inf %>% filter(UF==24, informal==0), "Rio Grande do Norte","Ocupados - Formais"),
    monta(dsg_inf %>% filter(UF==24, informal==1), "Rio Grande do Norte","Ocupados - Informais")
  )
}

# ==== K) Renda (Rend_H_real) — média/mediana — Formais vs Informais
calc_renda_formal_informal <- function(dsg, tri, ano){
  dsg_inf <- dsg %>% cria_informal()
  sumariza <- function(subd, local, grp){
    subd %>% filter(VD4001==1, VD4002==1, !is.na(Rend_H_real), Rend_H_real>0) %>%
      summarise(
        media   = survey_mean(Rend_H_real, na.rm=TRUE),
        mediana = survey_median(Rend_H_real, na.rm=TRUE),
        n       = unweighted(n())
      ) %>% transmute(trimestre=rotulo_tri(tri,ano), local=local, grupo=grp,
                      media=round(media,0), mediana=round(mediana,0), n=n,
                      def_renda="VD4016*Habitual>0", def_ocup="VD4001==1 & VD4002==1")
  }
  dplyr::bind_rows(
    sumariza(dsg_inf %>% filter(informal==0), "Brasil","Formais"),
    sumariza(dsg_inf %>% filter(informal==1), "Brasil","Informais"),
    sumariza(dsg_inf %>% filter(UF %in% nordeste_ufs, informal==0), "Nordeste","Formais"),
    sumariza(dsg_inf %>% filter(UF %in% nordeste_ufs, informal==1), "Nordeste","Informais"),
    sumariza(dsg_inf %>% filter(UF==24, informal==0), "Rio Grande do Norte","Formais"),
    sumariza(dsg_inf %>% filter(UF==24, informal==1), "Rio Grande do Norte","Informais")
  )
}

# ==== L) Horas habituais/efetivas — Formais vs Informais
calc_horas_formal_informal <- function(dsg, tri, ano){
  dsg_inf <- dsg %>% cria_informal()
  sumariza <- function(subd, local, grp){
    subd %>% filter(VD4001==1, VD4002==1) %>%
      summarise(horas_hab=survey_mean(VD4031,na.rm=TRUE),
                horas_eff=survey_mean(VD4035,na.rm=TRUE)) %>%
      transmute(trimestre=rotulo_tri(tri,ano), local=local, grupo=grp,
                horas_hab=round(horas_hab,1), horas_eff=round(horas_eff,1),
                def_horas_hab="VD4031", def_horas_eff="VD4035")
  }
  dplyr::bind_rows(
    sumariza(dsg_inf %>% filter(informal==0), "Brasil","Formais"),
    sumariza(dsg_inf %>% filter(informal==1), "Brasil","Informais"),
    sumariza(dsg_inf %>% filter(UF %in% nordeste_ufs, informal==0), "Nordeste","Formais"),
    sumariza(dsg_inf %>% filter(UF %in% nordeste_ufs, informal==1), "Nordeste","Informais"),
    sumariza(dsg_inf %>% filter(UF==24, informal==0), "Rio Grande do Norte","Formais"),
    sumariza(dsg_inf %>% filter(UF==24, informal==1), "Rio Grande do Norte","Informais")
  )
}

# ==== M) RN — Subocupação / Tx composta / Previdência por região
calc_regioesRN_subocup <- function(dsg, tri, ano){
  dsg %>% filter(UF==24, !is.na(regioes_rn)) %>% group_by(regioes_rn) %>%
    summarise(PEA=survey_total(VD4001==1,na.rm=TRUE),
              subocup=survey_total(VD4004A==1,na.rm=TRUE)) %>%
    transmute(trimestre=rotulo_tri(tri,ano), local=regioes_rn,
              subocup_k=round(subocup/1000,1), PEA_k=round(PEA/1000,1),
              tx_subocup=round(100*subocup/pmax(PEA,1),1),
              definicao_subocup="VD4004A==1", definicao_PEA="VD4001==1")
}
calc_regioesRN_txcomp <- function(dsg, tri, ano){
  dsg %>% filter(UF==24, !is.na(regioes_rn)) %>% group_by(regioes_rn) %>%
    summarise(desocup=survey_total(VD4002==2,na.rm=TRUE),
              subocup=survey_total(VD4004A==1,na.rm=TRUE),
              FTP    =survey_total(VD4003==1,na.rm=TRUE),
              PEA    =survey_total(VD4001==1,na.rm=TRUE)) %>%
    transmute(trimestre=rotulo_tri(tri,ano), local=regioes_rn,
              numerador_k=round((desocup+subocup+FTP)/1000,1),
              denominador_k=round((PEA+FTP)/1000,1),
              tx_composta=round(100*(desocup+subocup+FTP)/pmax(PEA+FTP,1),1),
              num_formula="(VD4002==2)+(VD4004A==1)+(VD4003==1)",
              den_formula="(VD4001==1)+(VD4003==1)")
}
calc_regioesRN_previdencia <- function(dsg, tri, ano){
  dsg_inf <- dsg %>% cria_informal()
  total <- dsg %>% filter(UF==24,!is.na(regioes_rn),VD4001==1,VD4002==1) %>%
    group_by(regioes_rn) %>%
    summarise(ocup=survey_total(na.rm=TRUE), contrib=survey_total(VD4012==1,na.rm=TRUE)) %>%
    transmute(trimestre=rotulo_tri(tri,ano), local=regioes_rn, grupo="Ocupados - Total",
              pct_contrib=round(100*contrib/pmax(ocup,1),1),
              ocup_k=round(ocup/1000,1), contrib_k=round(contrib/1000,1))
  form_inf <- dsg_inf %>% filter(UF==24,!is.na(regioes_rn),VD4001==1,VD4002==1) %>%
    mutate(grupo=ifelse(informal==1,"Ocupados - Informais","Ocupados - Formais")) %>%
    group_by(regioes_rn, grupo) %>%
    summarise(ocup=survey_total(na.rm=TRUE), contrib=survey_total(VD4012==1,na.rm=TRUE), .groups="drop") %>%
    transmute(trimestre=rotulo_tri(tri,ano), local=regioes_rn, grupo=grupo,
              pct_contrib=round(100*contrib/pmax(ocup,1),1),
              ocup_k=round(ocup/1000,1), contrib_k=round(contrib/1000,1))
  dplyr::bind_rows(total, form_inf)
}

# ==== N) Gaps RN – Brasil
calc_gap_RN_BR <- function(dsg, tri, ano, var=c("sexo","idade","raca","escolar")){
  comp <- calc_inf_por_grupo(dsg, tri, ano, var = match.arg(var))
  chave <- setdiff(names(comp),
                   c("trimestre","local","ocupados_k","informais_k","formais_k","tx_informalidade"))[1]
  wide <- comp %>%
    dplyr::select(trimestre, local, !!chave, tx_informalidade) %>%
    tidyr::pivot_wider(names_from = local, values_from = tx_informalidade)
  if (!all(c("Brasil","Rio Grande do Norte") %in% names(wide))) return(tibble())
  wide %>% mutate(gap_pp = `Rio Grande do Norte` - Brasil)
}



# ============================================================
# PASSO 3 — Execução Única por trimestre + exportações CSV
# ============================================================

method_design <- "classic"  # use "rep" para desenho com réplicas

run_tudo_trimestre <- function(tri, ano){
  dsg <- importa_pnad_design(tri, ano, method = method_design)
  on.exit({ rm(dsg); gc() }, add = TRUE)
  
  list(
    # Núcleo
    mercado_basico  = calc_mercado_basico(dsg, tri, ano),
    inf_total_loc   = calc_inf_total_locais(dsg, tri, ano),
    inf_sexo        = calc_inf_por_grupo(dsg, tri, ano, "sexo"),
    inf_idade       = calc_inf_por_grupo(dsg, tri, ano, "idade"),
    inf_raca        = calc_inf_por_grupo(dsg, tri, ano, "raca"),
    inf_escolar     = calc_inf_por_grupo(dsg, tri, ano, "escolar"),
    inf_setor       = calc_inf_por_setor(dsg, tri, ano),
    mix_setor_inf   = calc_mix_setorial_informais(dsg, tri, ano),
    rnreg_inf       = calc_inf_regioesRN(dsg, tri, ano),
    
    # Subutilização
    subocup         = calc_subocupacao(dsg, tri, ano),
    ftp_desalento   = calc_ftp_desalento(dsg, tri, ano),
    tx_composta     = calc_tx_composta(dsg, tri, ano),
    
    # Previdência / Renda / Horas
    previdencia     = calc_previdencia(dsg, tri, ano),
    renda_form_inf  = calc_renda_formal_informal(dsg, tri, ano),  # Rend_H_real
    horas_form_inf  = calc_horas_formal_informal(dsg, tri, ano),
    
    # Versões regionais RN
    rnreg_subocup   = calc_regioesRN_subocup(dsg, tri, ano),
    rnreg_txcomp    = calc_regioesRN_txcomp(dsg, tri, ano),
    rnreg_previd    = calc_regioesRN_previdencia(dsg, tri, ano),
    
    # Gaps RN-BR
    gap_sexo        = calc_gap_RN_BR(dsg, tri, ano, "sexo"),
    gap_idade       = calc_gap_RN_BR(dsg, tri, ano, "idade"),
    gap_raca        = calc_gap_RN_BR(dsg, tri, ano, "raca"),
    gap_escolar     = calc_gap_RN_BR(dsg, tri, ano, "escolar")
  )
}

# Rodar todos os trimestres (UM import por trimestre)
res <- lapply(trimestres, \(t) run_tudo_trimestre(t$tri, t$ano))

# =========================
# Exports (tabelas principais)
# =========================

# T1. Nível e taxa de informalidade — total e recortes (empilha todas)
tb_inf_total     <- bind_rows(lapply(res, \(x) x$inf_total_loc))
tb_inf_sexo      <- bind_rows(lapply(res, \(x) x$inf_sexo))
tb_inf_idade     <- bind_rows(lapply(res, \(x) x$inf_idade))
tb_inf_raca      <- bind_rows(lapply(res, \(x) x$inf_raca))
tb_inf_escolar   <- bind_rows(lapply(res, \(x) x$inf_escolar))

# T2. Posição na ocupação / Setor (níveis e taxas dos informais por VD4010)
tb_inf_setor     <- bind_rows(lapply(res, \(x) x$inf_setor))
tb_mix_setor_inf <- bind_rows(lapply(res, \(x) x$mix_setor_inf))

# T3. Regiões do RN — informalidade
tb_rnreg_inf     <- bind_rows(lapply(res, \(x) x$rnreg_inf))

# T4. Subocupação e Subutilização
tb_subocup       <- bind_rows(lapply(res, \(x) x$subocup))
tb_ftp_desal     <- bind_rows(lapply(res, \(x) x$ftp_desalento))
tb_tx_comp       <- bind_rows(lapply(res, \(x) x$tx_composta))

# T5. Renda (média e mediana) — formais vs informais — deflacionada
tb_renda         <- bind_rows(lapply(res, \(x) x$renda_form_inf))

# T6. Horas — formais vs informais
tb_horas         <- bind_rows(lapply(res, \(x) x$horas_form_inf))

# T7. Previdência — % contribui
tb_prev          <- bind_rows(lapply(res, \(x) x$previdencia))

# T8. RN — Subocupação, Tx composta e Previdência por região
tb_rnreg_subocup <- bind_rows(lapply(res, \(x) x$rnreg_subocup))
tb_rnreg_txcomp  <- bind_rows(lapply(res, \(x) x$rnreg_txcomp))
tb_rnreg_prev    <- bind_rows(lapply(res, \(x) x$rnreg_previd))

# T9. Gaps RN-BR (p.p.)
tb_gap_sexo      <- bind_rows(lapply(res, \(x) x$gap_sexo))
tb_gap_idade     <- bind_rows(lapply(res, \(x) x$gap_idade))
tb_gap_raca      <- bind_rows(lapply(res, \(x) x$gap_raca))
tb_gap_escolar   <- bind_rows(lapply(res, \(x) x$gap_escolar))

# =========================
# Gravação
# =========================
write_csv2(tb_inf_total,     file.path(dir_out, "T1_informalidade_total.csv"))
write_csv2(tb_inf_sexo,      file.path(dir_out, "T1a_informalidade_por_sexo.csv"))
write_csv2(tb_inf_idade,     file.path(dir_out, "T1b_informalidade_por_idade.csv"))
write_csv2(tb_inf_raca,      file.path(dir_out, "T1c_informalidade_por_raca.csv"))
write_csv2(tb_inf_escolar,   file.path(dir_out, "T1d_informalidade_por_escolaridade.csv"))

write_csv2(tb_inf_setor,     file.path(dir_out, "T2_informalidade_por_setor.csv"))
write_csv2(tb_mix_setor_inf, file.path(dir_out, "T2b_mix_setorial_informais.csv"))

write_csv2(tb_rnreg_inf,     file.path(dir_out, "T3_informalidade_regioes_RN.csv"))

write_csv2(tb_subocup,       file.path(dir_out, "T4_subocupacao.csv"))
write_csv2(tb_ftp_desal,     file.path(dir_out, "T4b_forca_trabalho_potencial_e_desalento.csv"))
write_csv2(tb_tx_comp,       file.path(dir_out, "T4c_taxa_composta_subutilizacao.csv"))

write_csv2(tb_renda,         file.path(dir_out, "T5_renda_formais_informais_deflacionada.csv"))
write_csv2(tb_horas,         file.path(dir_out, "T6_horas_formais_informais.csv"))
write_csv2(tb_prev,          file.path(dir_out, "T7_previdencia_contribuicao.csv"))

write_csv2(tb_rnreg_subocup, file.path(dir_out, "T8a_RN_regioes_subocupacao.csv"))
write_csv2(tb_rnreg_txcomp,  file.path(dir_out, "T8b_RN_regioes_tx_composta.csv"))
write_csv2(tb_rnreg_prev,    file.path(dir_out, "T8c_RN_regioes_previdencia.csv"))

write_csv2(tb_gap_sexo,      file.path(dir_out, "T9_gap_RN_BR_sexo.csv"))
write_csv2(tb_gap_idade,     file.path(dir_out, "T9_gap_RN_BR_idade.csv"))
write_csv2(tb_gap_raca,      file.path(dir_out, "T9_gap_RN_BR_raca.csv"))
write_csv2(tb_gap_escolar,   file.path(dir_out, "T9_gap_RN_BR_escolaridade.csv"))

# Visualização rápida (opcional)
# View(tb_inf_total); View(tb_renda)
