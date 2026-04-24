import pandas as pd
import requests
import io
import os
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URLs Diretas das 11 Bases extraídas do Dados.gov.br
# Filtro de UF do Nordeste para otimizar a extração
NE_FILTER = "&q=sigla_uf:(MA%20OR%20PI%20OR%20CE%20OR%20RN%20OR%20PB%20OR%20PE%20OR%20AL%20OR%20SE%20OR%20BA)"

URLS = {
    "BASE_01_TERMO_ADESAO_FINANCEIRO": "https://mdsgov.sharepoint.com/:x:/s/DesenvolvimentoSocial-CinciadeDados/IQB9Dd2Sv5qhSbbT3Fqp3S0VARzqtYgc2k_Iuvx6bo2at_A?download=1",
    "BASE_02_MUNICIPIOS_ADESAO": f"https://aplicacoes.mds.gov.br/sagi/servicos/misocial/?fq=anomes_s%3A%20%5B202201%20TO%20*%5D{NE_FILTER}&rows=1000000&wt=csv&fl=codigo_ibge,anomes_s,sigla_uf,municipio,paa_indicador_adesao_municipio_i",
    "BASE_03_EXECUCAO_GERAL": f"https://aplicacoes.mds.gov.br/sagi/servicos/misocial/?fq=anomes_s%3A%20%5B201101%20TO%20*%5D{NE_FILTER}&rows=1000000&wt=csv&fl=codigo_ibge,anomes_s,agricultores_fornec_paa_i,recur_pagos_agricul_paa_f",
    "BASE_04_PERFIL_SEXO": f"https://aplicacoes.mds.gov.br/sagi/servicos/misocial/?fq=anomes_s%3A%20%5B201412%20TO%20*%5D{NE_FILTER}&rows=1000000&wt=csv&fl=codigo_ibge,anomes_s,paa_qtd_agricul_familiar_sexo_masculino_i,paa_qtd_agricul_familiar_sexo_feminino_i,paa_qtd_agricul_familiar_sem_info_sexo_i",
    "BASE_05_COMPRA_DOACAO_ADESAO": f"https://aplicacoes.mds.gov.br/sagi/servicos/misocial/?fq=anomes_s%3A%20%5B202101%20TO%20*%5D{NE_FILTER}&rows=1000000&wt=csv&fl=codigo_ibge,anomes_s,paa_qtd_agricul_familiar_exec_compra_doacao_simul_i,paa_vlr_pago_exec_compra_doacao_simul_d,paa_qtd_alim_adquiridos_exec_compra_doacao_simul_d",
    "BASE_06_LEITE_ADESAO": f"https://aplicacoes.mds.gov.br/sagi/servicos/misocial/?fq=anomes_s%3A%20%5B202101%20TO%20*%5D{NE_FILTER}&rows=1000000&wt=csv&fl=codigo_ibge,anomes_s,paa_qtd_agricul_familiar_exec_incentivo_leite_i,paa_vlr_pago_exec_incentivo_leite_d,paa_qtd_alim_adquiridos_exec_incentivo_leite_i",
    "BASE_07_MODAL_DOACAO": f"https://aplicacoes.mds.gov.br/sagi/servicos/misocial/?fq=anomes_s%3A%20%5B201101%20TO%20*%5D{NE_FILTER}&rows=1000000&wt=csv&fl=codigo_ibge,anomes_s,paa_qtd_agricul_familiar_modal_compra_doacao_simul_i",
    "BASE_08_MODAL_LEITE": f"https://aplicacoes.mds.gov.br/sagi/servicos/misocial/?fq=anomes_s%3A%20%5B201101%20TO%20*%5D{NE_FILTER}&rows=1000000&wt=csv&fl=codigo_ibge,anomes_s,paa_qtd_agricul_familiar_modal_incentivo_leite_i",
    "BASE_09_MODAL_COMPRA_DIRETA": f"https://aplicacoes.mds.gov.br/sagi/servicos/misocial/?fq=anomes_s%3A%20%5B201101%20TO%20*%5D{NE_FILTER}&rows=1000000&wt=csv&fl=codigo_ibge,anomes_s,paa_qtd_agricul_familiar_modal_compra_direta_i",
    "BASE_10_MODAL_ESTOQUE": f"https://aplicacoes.mds.gov.br/sagi/servicos/misocial/?fq=anomes_s%3A%20%5B201101%20TO%20*%5D{NE_FILTER}&rows=1000000&wt=csv&fl=codigo_ibge,anomes_s,paa_qtd_agricul_familiar_modal_formacao_estoque_i",
    "BASE_11_MODAL_SEMENTES": f"https://aplicacoes.mds.gov.br/sagi/servicos/misocial/?fq=anomes_s%3A%20%5B201501%20TO%20*%5D{NE_FILTER}&rows=1000000&wt=csv&fl=codigo_ibge,anomes_s,paa_qtd_agricul_familiar_modal_aquisicao_sementes_i"
}

OUTPUT_REPORT = "outputs/paa_reports/PAA_TOTAL_EXAUSTIVO_11_BASES.xlsx"
os.makedirs("outputs/paa_reports", exist_ok=True)

def fetch_and_consolidate():
    print(f"🚀 Iniciando Consolidação das 11 Bases PAA - {datetime.now()}")
    writer = pd.ExcelWriter(OUTPUT_REPORT, engine='xlsxwriter')
    
    master_df = None

    for name, url in URLS.items():
        print(f"   -> Processando {name}...")
        try:
            if "sharepoint.com" in url:
                # Base 1 - Financeiro Termo de Adesão (Pactuado, Portaria, etc)
                resp = requests.get(url, verify=False)
                df = pd.read_excel(io.BytesIO(resp.content))
            else:
                resp = requests.get(url, verify=False)
                df = pd.read_csv(io.StringIO(resp.text))
            
            # Limpeza
            df['ano'] = df['anomes_s'].astype(str).str[:4] if 'anomes_s' in df.columns else None
            df.to_excel(writer, sheet_name=name[:31], index=False)
            print(f"      → {name}: {len(df)} registros processados.")
            
            # Merge Progressivo na Master (por IBGE e AnoMes)
            if 'codigo_ibge' in df.columns and 'anomes_s' in df.columns:
                print(f"      → Integrando {name} na Master...")
                if master_df is None:
                    master_df = df
                else:
                    # Garantir que codigo_ibge e anomes_s sejam strings para merge seguro
                    df['codigo_ibge'] = df['codigo_ibge'].astype(str)
                    df['anomes_s'] = df['anomes_s'].astype(str)
                    master_df['codigo_ibge'] = master_df['codigo_ibge'].astype(str)
                    master_df['anomes_s'] = master_df['anomes_s'].astype(str)

                    cols_to_use = [c for c in df.columns if c not in master_df.columns or c in ['codigo_ibge', 'anomes_s']]
                    master_df = pd.merge(master_df, df[cols_to_use], on=['codigo_ibge', 'anomes_s'], how='outer')
                print(f"      → Master atual: {len(master_df)} registros.")
        except Exception as e:
            print(f"   ❌ Erro em {name}: {e}")

    if master_df is not None:
        master_df.to_excel(writer, sheet_name='MASTER_INTEGRADA', index=False)
    
    writer.close()
    print(f"✅ Arquivo gerado: {OUTPUT_REPORT}")

if __name__ == "__main__":
    fetch_and_consolidate()
