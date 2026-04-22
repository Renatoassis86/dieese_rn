# ============================================================
# Estudo — Informalidade & Subutilização (RN, 2019T4–2025T2)
# Saídas: D:/repositorio_geral/pnad_continua/estudo_informalidade_2025
# Cache : D:/pnad_temp  (cada trimestre baixado 1x e reaproveitado)
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

options(survey.lonely.psu = "adjust")   # PSU única
options(timeout = 600)

# Diretórios
dir_temp_base <- "D:/pnad_temp"
dir_out       <- "D:/repositorio_geral/pnad_continua/estudo_informalidade_2025"
dir.create(dir_temp_base, showWarnings = FALSE, recursive = TRUE)
dir.create(dir_out,       showWarnings = FALSE, recursive = TRUE)

# Trimestres
trimestres <- list(
  list(tri = 4, ano = 2019),
  list(tri = 4, ano = 2020),
  list(tri = 4, ano = 2021),
  list(tri = 4, ano = 2022),
  list(tri = 4, ano = 2023),
  list(tri = 4, ano = 2024),
  list(tri = 2, ano = 2025)
)

# Utilitários
rotulo_tri   <- function(tri, ano) sprintf("%dº tri/%d", tri, ano)
nordeste_ufs <- c(21,22,23,24,25,26,27,28,29)  # MA..BA

mapa_regioes_rn <- function(estrato) {
  ce <- trunc(estrato/1000)
  dplyr::case_when(
    ce == 2410 ~ "Natal(RN)",
    ce == 2420 ~ "Entorno metropolitano de Natal(RN)",
    ce == 2451 ~ "Agreste do RN",
    ce == 2452 ~ "Oeste do RN",
    ce == 2453 ~ "Central do RN",
    TRUE ~ NA_character_
  )
}

# --------- Rótulos: VD4010 (setores) e VD4009 (posição) ----------
rotulos_vd4010 <- c(
  "1"="Agricultura, pecuária, produção florestal, pesca e aquicultura",
  "2"="Indústria geral",
  "3"="Construção",
  "4"="Comércio, reparação de veículos automotores e motocicletas",
  "5"="Transporte, armazenagem e correio",
  "6"="Alojamento e alimentação",
  "7"="Informação, comunicação e atv. financeiras/imobiliárias/profissionais/administrativas",
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

lbl_sexo   <- function(v) ifelse(v==1,"Homem","Mulher")
faixa_idade <- function(idade) dplyr::case_when(
  idade >= 14 & idade <= 24 ~ "14–24",
  idade >= 25 & idade <= 39 ~ "25–39",
  idade >= 40 & idade <= 59 ~ "40–59",
  idade >= 60               ~ "60+",
  TRUE ~ NA_character_
)
lbl_raca <- function(v) dplyr::case_when(
  v == 1 ~ "Branco",
  v == 2 ~ "Preto",
  v %in% c(3,4,5) ~ "Demais Raças",
  TRUE ~ NA_character_
)
lbl_escolar <- function(vd3004){
  dplyr::case_when(
    vd3004 %in% c(1,2)   ~ "Fundamental ou menos",
    vd3004 %in% c(3,4)   ~ "Médio",
    vd3004 %in% c(5,6,7) ~ "Superior",
    TRUE ~ NA_character_
  )
}

# --------- Desenhos amostrais (como no seu exemplo) ----------
faz_desenho_amostral_rep <- function(df){
  des <- survey::svrepdesign(
    data = df,
    weights = ~V1028,
    type = "bootstrap",
    repweights = "V1028[0-9]+",  # colunas V1028###
    mse = TRUE,
    replicates = length(sprintf("V1028%03d", 1:200)),
    df = length(sprintf("V1028%03d", 1:200))
  )
  srvyr::as_survey_rep(des)
}
faz_desenho_amostral_classic <- function(df){
  df %>% srvyr::as_survey_design(ids = UPA, strata = Estrato, weights = V1028, nest = TRUE)
}

# --------- Importador ÚNICO (com deflator Habitual) ----------
# method = "classic" (padrão) ou "rep" para réplicas
importa_pnad_design <- function(tri, ano, method = c("classic","rep")){
  method <- match.arg(method)
  vars <- c(
    "Ano","Trimestre","UF","Estrato","UPA","V1028",
    "V2007","V2009","V2010","VD3004",             # recortes
    "VD4001","VD4002","VD4003","VD4004A","VD4005",# subutilização
    "V4010","VD4009","V4012","V4019","V4029","VD4012", # setor/posição/formalidad/previd
    "VD4016","VD4031","VD4035", "Habitual"        # renda, horas e deflator
  )
  savedir <- file.path(dir_temp_base, sprintf("PNADC_%02d%d", tri, ano))
  if (!dir.exists(savedir)) dir.create(savedir, recursive = TRUE, showWarnings = FALSE)
  
  # baixa 1x e reusa do savedir
  df <- PNADcIBGE::get_pnadc(
    year    = ano, quarter = tri,
    vars    = vars,
    labels  = FALSE, design = FALSE,
    savedir = savedir
  )
  
  stopifnot(is.data.frame(df))
  falt <- setdiff(vars, names(df))
  if(length(falt)) stop("Variáveis ausentes: ", paste(falt, collapse=", "))
  
  # Deflator e rótulos auxiliares
  df <- df %>%
    mutate(
      regioes_rn  = mapa_regioes_rn(Estrato),
      Rend_H_real = VD4016 * Habitual,
      setor_lbl   = dplyr::recode(as.character(V4010), !!!rotulos_vd4010, .default = NA_character_),
      pos_ocup    = dplyr::recode(as.character(VD4009), !!!rotulos_vd4009, .default = NA_character_)
    )
  
  # Desenho
  if (method == "rep") {
    # mantém colunas de réplica V1028### se existirem no arquivo
    dsg <- faz_desenho_amostral_rep(df)
  } else {
    # remove réplicas caso venham (economiza RAM) e usa desenho clássico
    c_drop <- intersect(names(df), sprintf("V1028%03d", 1:200))
    if (length(c_drop)) df <- dplyr::select(df, -dplyr::all_of(c_drop))
    dsg <- faz_desenho_amostral_classic(df)
  }
  dsg
}

# Regra de informalidade (OIT/IBGE)
cria_informal <- function(dsg){
  dsg %>% mutate(informal = dplyr::case_when(
    V4012 == 3 & V4029 == 2 ~ 1,  # empregado privado sem carteira
    V4012 == 1 & V4029 == 2 ~ 1,  # doméstico sem carteira
    V4012 == 5 & V4019 == 2 ~ 1,  # empregador sem CNPJ
    V4012 == 6 & V4019 == 2 ~ 1,  # conta-própria sem CNPJ
    V4012 == 7              ~ 1,  # familiar auxiliar
    TRUE ~ 0
  ))
}


# ============================================================
# Funções de cálculo — SEM novo download
# ============================================================

# Mercado básico
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

# Informalidade total — BR/NE/RN
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

# Por grupo (sexo/idade/raça/escolaridade)
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

# Por setor/atividade (VD4010) e distribuição dos informais
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

# Informalidade — Regiões do RN
calc_inf_regioesRN <- function(dsg, tri, ano){
  dsg %>% filter(UF==24, !is.na(regioes_rn), VD4002==1) %>% cria_informal() %>%
    group_by(regioes_rn) %>%
    summarise(ocup=survey_total(na.rm=TRUE), inf=survey_total(informal,na.rm=TRUE), .groups="drop") %>%
    transmute(trimestre=rotulo_tri(tri,ano), local=regioes_rn,
              ocupados_k=round(ocup/1000,1), informais_k=round(inf/1000,1),
              formais_k=round((ocup-inf)/1000,1),
              tx_informalidade=round(100*inf/pmax(ocup,1),1))
}

# Subocupação / FTP / Tx composta
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
calc_tx_composta <- function(dsg, tri, ano){
  monta <- function(subd, local){
    subd %>% summarise(
      desocup=survey_total(VD4002==2,na.rm=TRUE),
      subocup=survey_total(VD4004A==1,na.rm=TRUE),
      FTP=survey_total(VD4003==1,na.rm=TRUE),
      PEA=survey_total(VD4001==1,na.rm=TRUE)
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

# Previdência (% contribui) — total e por formalidade
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

# Renda (DEFLACIONADA: Rend_H_real) — Formais x Informais
calc_renda_formal_informal <- function(dsg, tri, ano){
  dsg_inf <- dsg %>% cria_informal()
  sumariza <- function(subd, local, grp){
    subd %>% filter(VD4001==1, VD4002==1, !is.na(Rend_H_real), Rend_H_real>0) %>%
      summarise(
        media   = survey_mean(Rend_H_real, na.rm=TRUE),
        mediana = survey_median(Rend_H_real, na.rm=TRUE),
        p25     = survey_quantile(Rend_H_real, 0.25, na.rm=TRUE),
        p75     = survey_quantile(Rend_H_real, 0.75, na.rm=TRUE),
        n       = unweighted(n())
      ) %>% transmute(trimestre=rotulo_tri(tri,ano), local=local, grupo=grp,
                      media=round(media,0), mediana=round(mediana,0),
                      p25=round(p25,0), p75=round(p75,0), n=n)
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

# Horas — Formais x Informais
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

# RN — Subocupação, Tx composta e Previdência por região
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
              FTP=survey_total(VD4003==1,na.rm=TRUE),
              PEA=survey_total(VD4001==1,na.rm=TRUE)) %>%
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

# Gap RN – Brasil (p.p.) por grupo
calc_gap_RN_BR <- function(dsg, tri, ano, var=c("sexo","idade","raca","escolar")){
  comp <- calc_inf_por_grupo(dsg, tri, ano, var = match.arg(var))
  chave <- setdiff(names(comp), c("trimestre","local","ocupados_k","informais_k","formais_k","tx_informalidade"))[1]
  wide <- comp %>%
    dplyr::select(trimestre, local, !!chave, tx_informalidade) %>%
    tidyr::pivot_wider(names_from = local, values_from = tx_informalidade)
  if(!all(c("Brasil","Rio Grande do Norte") %in% names(wide))) return(tibble())
  wide %>% mutate(gap_pp = `Rio Grande do Norte` - Brasil)
}


# ============================================================
# Execução — UM import por trimestre -> calcula tudo
# defina method = "classic" ou "rep"
# ============================================================
method_design <- "classic"   # mude para "rep" se quiser réplicas

run_tudo_trimestre <- function(tri, ano){
  dsg <- importa_pnad_design(tri, ano, method = method_design)
  on.exit({ rm(dsg); gc() }, add = TRUE)
  
  list(
    mercado_basico  = calc_mercado_basico(dsg, tri, ano),
    inf_total_loc   = calc_inf_total_locais(dsg, tri, ano),
    inf_sexo        = calc_inf_por_grupo(dsg, tri, ano, "sexo"),
    inf_idade       = calc_inf_por_grupo(dsg, tri, ano, "idade"),
    inf_raca        = calc_inf_por_grupo(dsg, tri, ano, "raca"),
    inf_escolar     = calc_inf_por_grupo(dsg, tri, ano, "escolar"),
    inf_setor       = calc_inf_por_setor(dsg, tri, ano),
    mix_setor_inf   = calc_mix_setorial_informais(dsg, tri, ano),
    rnreg_inf       = calc_inf_regioesRN(dsg, tri, ano),
    
    subocup         = calc_subocupacao(dsg, tri, ano),
    ftp_desalento   = calc_ftp_desalento(dsg, tri, ano),
    tx_composta     = calc_tx_composta(dsg, tri, ano),
    previdencia     = calc_previdencia(dsg, tri, ano),
    renda_form_inf  = calc_renda_formal_informal(dsg, tri, ano),  # já deflacionada
    horas_form_inf  = calc_horas_formal_informal(dsg, tri, ano),
    
    rnreg_subocup   = calc_regioesRN_subocup(dsg, tri, ano),
    rnreg_txcomp    = calc_regioesRN_txcomp(dsg, tri, ano),
    rnreg_previd    = calc_regioesRN_previdencia(dsg, tri, ano),
    
    gap_sexo        = calc_gap_RN_BR(dsg, tri, ano, "sexo"),
    gap_idade       = calc_gap_RN_BR(dsg, tri, ano, "idade"),
    gap_raca        = calc_gap_RN_BR(dsg, tri, ano, "raca"),
    gap_escolar     = calc_gap_RN_BR(dsg, tri, ano, "escolar")
  )
}

# Rodar
res <- lapply(trimestres, \(t) run_tudo_trimestre(t$tri, t$ano))

# Empilhar
tb_mercado_basico   <- bind_rows(lapply(res, \(x) x$mercado_basico))
tb_inf_total_loc    <- bind_rows(lapply(res, \(x) x$inf_total_loc))
tb_inf_sexo         <- bind_rows(lapply(res, \(x) x$inf_sexo))
tb_inf_idade        <- bind_rows(lapply(res, \(x) x$inf_idade))
tb_inf_raca         <- bind_rows(lapply(res, \(x) x$inf_raca))
tb_inf_escolar      <- bind_rows(lapply(res, \(x) x$inf_escolar))
tb_inf_setor        <- bind_rows(lapply(res, \(x) x$inf_setor))
tb_mix_setor_inf    <- bind_rows(lapply(res, \(x) x$mix_setor_inf))
tb_rnreg_inf        <- bind_rows(lapply(res, \(x) x$rnreg_inf))

tb_subocup          <- bind_rows(lapply(res, \(x) x$subocup))
tb_ftp_desalento    <- bind_rows(lapply(res, \(x) x$ftp_desalento))
tb_tx_composta      <- bind_rows(lapply(res, \(x) x$tx_composta))
tb_previdencia      <- bind_rows(lapply(res, \(x) x$previdencia))
tb_renda_form_inf   <- bind_rows(lapply(res, \(x) x$renda_form_inf))
tb_horas_form_inf   <- bind_rows(lapply(res, \(x) x$horas_form_inf))

tb_rnreg_subocup    <- bind_rows(lapply(res, \(x) x$rnreg_subocup))
tb_rnreg_txcomp     <- bind_rows(lapply(res, \(x) x$rnreg_txcomp))
tb_rnreg_previd     <- bind_rows(lapply(res, \(x) x$rnreg_previd))

tb_gap_sexo         <- bind_rows(lapply(res, \(x) x$gap_sexo))
tb_gap_idade        <- bind_rows(lapply(res, \(x) x$gap_idade))
tb_gap_raca         <- bind_rows(lapply(res, \(x) x$gap_raca))
tb_gap_escolar      <- bind_rows(lapply(res, \(x) x$gap_escolar))

# Exportar
write_csv2(tb_mercado_basico, file.path(dir_out, "mercado_basico_BR_NE_RN_2019t4_2025t2.csv"))

write_csv2(tb_inf_total_loc,  file.path(dir_out, "informalidade_total_BR_NE_RN_2019t4_2025t2.csv"))
write_csv2(tb_inf_sexo,       file.path(dir_out, "informalidade_por_sexo_BR_NE_RN_2019t4_2025t2.csv"))
write_csv2(tb_inf_idade,      file.path(dir_out, "informalidade_por_faixa_BR_NE_RN_2019t4_2025t2.csv"))
write_csv2(tb_inf_raca,       file.path(dir_out, "informalidade_por_raca_BR_NE_RN_2019t4_2025t2.csv"))
write_csv2(tb_inf_escolar,    file.path(dir_out, "informalidade_por_escolaridade_BR_NE_RN_2019t4_2025t2.csv"))

write_csv2(tb_inf_setor,      file.path(dir_out, "informalidade_por_setor_VD4010_BR_NE_RN_2019t4_2025t2.csv"))
write_csv2(tb_mix_setor_inf,  file.path(dir_out, "mix_setorial_informais_VD4010_BR_NE_RN_2019t4_2025t2.csv"))
write_csv2(tb_rnreg_inf,      file.path(dir_out, "informalidade_total_REGIOES_RN_2019t4_2025t2.csv"))

write_csv2(tb_subocup,        file.path(dir_out, "subocupacao_BR_NE_RN_2019t4_2025t2.csv"))
write_csv2(tb_ftp_desalento,  file.path(dir_out, "ftp_desalento_BR_NE_RN_2019t4_2025t2.csv"))
write_csv2(tb_tx_composta,    file.path(dir_out, "tx_composta_subutilizacao_BR_NE_RN_2019t4_2025t2.csv"))

write_csv2(tb_previdencia,    file.path(dir_out, "previdencia_ocupados_formal_informal_BR_NE_RN_2019t4_2025t2.csv"))
write_csv2(tb_renda_form_inf, file.path(dir_out, "renda_real_Rend_H_real_formais_vs_informais_BR_NE_RN_2019t4_2025t2.csv"))
write_csv2(tb_horas_form_inf, file.path(dir_out, "horas_VD4031_VD4035_formais_vs_informais_BR_NE_RN_2019t4_2025t2.csv"))

write_csv2(tb_rnreg_subocup,  file.path(dir_out, "subocupacao_REGIOES_RN_2019t4_2025t2.csv"))
write_csv2(tb_rnreg_txcomp,   file.path(dir_out, "tx_composta_REGIOES_RN_2019t4_2025t2.csv"))
write_csv2(tb_rnreg_previd,   file.path(dir_out, "previdencia_REGIOES_RN_2019t4_2025t2.csv"))

write_csv2(tb_gap_sexo,       file.path(dir_out, "gap_RN_menos_BR_por_sexo_2019t4_2025t2.csv"))
write_csv2(tb_gap_idade,      file.path(dir_out, "gap_RN_menos_BR_por_faixa_2019t4_2025t2.csv"))
write_csv2(tb_gap_raca,       file.path(dir_out, "gap_RN_menos_BR_por_raca_2019t4_2025t2.csv"))
write_csv2(tb_gap_escolar,    file.path(dir_out, "gap_RN_menos_BR_por_escolaridade_2019t4_2025t2.csv"))
