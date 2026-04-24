import pandas as pd
import requests
import json
import os

SUPABASE_URL = "https://kyzcdpcmgiisllxmnhqn.supabase.co"
SUPABASE_KEY = "sb_publishable_DRWOVTb1-KWvTd35C_E18A_-L9RQtUJ"
OUTPUT_DIR = "outputs/paa_reports/estudos"

def export_paa_study_tables():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    print("🚀 Iniciando extração de dados para as tabelas de estudo do PAA (via REST API)...")
    
    # 1. Série Histórica RN (2011-2025)
    # Using the existing RPC get_paa_stats_annual
    url_rpc = f"{SUPABASE_URL}/rest/v1/rpc/get_paa_stats_annual"
    resp = requests.post(url_rpc, headers=headers, json={"uf_filter": "RN"})
    
    if resp.status_code == 200:
        data = resp.json()
        df_history = pd.DataFrame(data)
        # Sort and filter
        df_history = df_history[df_history['ano'] <= 2025].sort_values('ano')
        df_history.to_excel(f"{OUTPUT_DIR}/TABELA_01_PAA_RN_SERIE_HISTORICA_2011_2025.xlsx", index=False)
        print(f"✅ Tabela 01 (Série Histórica) exportada.")
    else:
        print(f"❌ Erro ao exportar Tabela 01: {resp.text}")

    # 2. Dados por Território (2024)
    url_terr = f"{SUPABASE_URL}/rest/v1/rpc/get_paa_stats_by_territory"
    resp_terr = requests.post(url_terr, headers=headers, json={"uf_filter": "RN", "year_filter": 2024})
    
    if resp_terr.status_code == 200:
        data_terr = resp_terr.json()
        df_territory = pd.DataFrame(data_terr)
        df_territory.to_excel(f"{OUTPUT_DIR}/TABELA_02_PAA_RN_TERRITORIOS_2024.xlsx", index=False)
        print(f"✅ Tabela 02 (Impacto Territorial 2024) exportada.")
    else:
        print(f"❌ Erro ao exportar Tabela 02: {resp_terr.text}")

    print("\n📊 Processo concluído. As tabelas estão disponíveis em /outputs/paa_reports/estudos/")
    print("👉 Estas tabelas contêm os indicadores permanentes para a narrativa do Observatório.")

if __name__ == "__main__":
    export_paa_study_tables()
