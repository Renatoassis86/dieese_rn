import pandas as pd
import requests
import io
import os
import urllib3
from datetime import datetime

# Configurações
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
MDS_API_URL = "https://aplicacoes.mds.gov.br/sagi/servicos/misocial/"
SUPABASE_URL = "https://kyzcdpcmgiisllxmnhqn.supabase.co"
SUPABASE_KEY = "sb_publishable_DRWOVTb1-KWvTd35C_E18A_-L9RQtUJ"

# Toda a lista de variáveis do Dicionário PAA + Metadados MDS
SOLR_FIELDS = [
    "codigo_ibge", "anomes_s", "sigla_uf",
    "agricultores_fornec_paa_i", "recur_pagos_agricul_paa_f",
    "paa_qtd_agricul_familiar_sexo_masculino_i", "paa_qtd_agricul_familiar_sexo_feminino_i",
    "paa_qtd_agricul_familiar_sem_info_sexo_i",
    "paa_vlr_pago_exec_compra_doacao_simul_d", "paa_qtd_agricul_familiar_modal_compra_doacao_simul_i",
    "paa_qtd_alim_adquiridos_exec_compra_doacao_simul_d",
    "paa_vlr_pago_exec_incentivo_leite_d", "paa_qtd_agricul_familiar_exec_incentivo_leite_i",
    "paa_qtd_alim_adquiridos_exec_incentivo_leite_i",
    "paa_indicador_adesao_municipio_i"
]

UF_NE = {'21': 'MA', '22': 'PI', '23': 'CE', '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL', '28': 'SE', '29': 'BA'}

def sync_all_paa():
    print(f"🔄 Iniciando Sincronização Exaustiva PAA - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    all_data = []
    for cod_uf, uf_name in UF_NE.items():
        print(f"   -> Extraindo {uf_name}...")
        url = f"{MDS_API_URL}?q=codigo_ibge:{cod_uf}*&rows=2000000&wt=csv&fl={','.join(SOLR_FIELDS)}"
        try:
            resp = requests.get(url, verify=False, timeout=300)
            df = pd.read_csv(io.StringIO(resp.text))
            all_data.append(df)
        except Exception as e:
            print(f"   ❌ Erro ao extrair {uf_name}: {e}")

    if not all_data: return

    df_full = pd.concat(all_data)
    df_full['ano'] = df_full['anomes_s'].astype(str).str[:4].astype(int)
    
    # Substituir NaNs por 0 para o banco
    numeric_cols = [c for c in SOLR_FIELDS if c not in ["codigo_ibge", "anomes_s", "sigla_uf"]]
    for c in numeric_cols: df_full[c] = pd.to_numeric(df_full[c], errors='coerce').fillna(0)

    # Agregação para o BI (Otimização: Ano x Município)
    # Queremos preservar o máximo de detalhe, então vamos agrupar por Ano/UF/Município
    print("📊 Agregando métricas anuais por município...")
    df_master = df_full.groupby(['codigo_ibge', 'ano', 'sigla_uf']).agg({
        'recur_pagos_agricul_paa_f': 'sum',
        'agricultores_fornec_paa_i': 'max',
        'paa_qtd_agricul_familiar_sexo_feminino_i': 'max',
        'paa_vlr_pago_exec_incentivo_leite_d': 'sum',
        'paa_vlr_pago_exec_compra_doacao_simul_d': 'sum',
        'paa_qtd_alim_adquiridos_exec_compra_doacao_simul_d': 'sum',
        'paa_qtd_alim_adquiridos_exec_incentivo_leite_i': 'sum'
    }).reset_index()
    
    df_master = df_master.rename(columns={
        'recur_pagos_agricul_paa_f': 'valor_pago',
        'agricultores_fornec_paa_i': 'agricultores',
        'paa_qtd_agricul_familiar_sexo_feminino_i': 'mulheres',
        'paa_vlr_pago_exec_incentivo_leite_d': 'valor_leite',
        'paa_vlr_pago_exec_compra_doacao_simul_d': 'valor_doacao',
        'paa_qtd_alim_adquiridos_exec_compra_doacao_simul_d': 'quilos_alimentos',
        'paa_qtd_alim_adquiridos_exec_incentivo_leite_i': 'litros_leite',
        'sigla_uf': 'uf'
    })

    # Upload para o Supabase (paa_master)
    # Nota: Precisamos garantir que a tabela tenha essas novas colunas de quilos/litros
    print("🚀 Ingerindo no Supabase...")
    records = df_master.to_dict('records')
    
    # Ingestão em lotes
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}
        requests.post(f"{SUPABASE_URL}/rest/v1/paa_master", headers=headers, json=batch)

    print("✅ Sincronização concluída com sucesso!")

if __name__ == "__main__":
    sync_all_paa()
