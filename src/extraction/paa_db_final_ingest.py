import pandas as pd
import requests
import json
import os

SUPABASE_URL = "https://kyzcdpcmgiisllxmnhqn.supabase.co"
SUPABASE_KEY = "sb_publishable_DRWOVTb1-KWvTd35C_E18A_-L9RQtUJ"
EXCEL_PATH = "outputs/paa_reports/PAA_TOTAL_EXAUSTIVO_11_BASES.xlsx"

def ingest_master():
    print(f"📥 Lendo Master Integrada de {EXCEL_PATH}...")
    try:
        # Tenta ler a aba master
        df = pd.read_excel(EXCEL_PATH, sheet_name='MASTER_INTEGRADA')
    except:
        print("   ⚠️ Aba MASTER_INTEGRADA não encontrada, tentando primeira aba...")
        df = pd.read_excel(EXCEL_PATH)

    # Mapeamento para o Banco (paa_master)
    # Incluindo campos da Base 1
    mapping = {
        'codigo_ibge': 'codigo_ibge',
        'anomes_s': 'anomes_s',
        'ano': 'ano',
        'sigla_uf': 'uf',
        'recur_pagos_agricul_paa_f': 'valor_pago',
        'paa_vlr_pago_exec_compra_doacao_simul_d': 'valor_doacao',
        'paa_vlr_pago_exec_incentivo_leite_d': 'valor_leite',
        'agricultores_fornec_paa_i': 'agricultores',
        'paa_qtd_agricul_familiar_sexo_feminino_i': 'mulheres',
        'paa_qtd_alim_adquiridos_exec_compra_doacao_simul_d': 'quilos_alimentos',
        'paa_qtd_alim_adquiridos_exec_incentivo_leite_i': 'litros_leite',
        # Base 1 Fields (Mapping potential names from SharePoint XLSX)
        'Valor pactuado': 'valor_pactuado',
        'Status': 'status_recurso',
        'Origem do orçamento': 'origem_orcamento',
        'Público atendido': 'publico_atendido',
        'Nº do plano operacional': 'n_plano_operacional',
        'Vigência': 'vigencia'
    }

    df = df.rename(columns=mapping)
    
    # Manter só os municípios do Nordeste (21-29)
    df['uf_code'] = df['codigo_ibge'].astype(str).str[:2]
    df = df[df['uf_code'].isin(['21','22','23','24','25','26','27','28','29'])]

    # Fill NaNs
    numeric_cols = ['valor_pago', 'valor_pactuado', 'valor_doacao', 'valor_leite', 'agricultores', 'mulheres', 'quilos_alimentos', 'litros_leite']
    for c in numeric_cols:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

    print(f"🚀 Ingerindo {len(df)} registros no Supabase...")
    
    records = df.to_dict('records')
    batch_size = 500
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }
        r = requests.post(f"{SUPABASE_URL}/rest/v1/paa_master", headers=headers, json=batch)
        if r.status_code >= 400:
            print(f"   ❌ Erro no lote {i}: {r.text}")

    print("✅ Ingestão Master Concluída!")

if __name__ == "__main__":
    if os.path.exists(EXCEL_PATH):
        ingest_master()
    else:
        print("❌ Arquivo Excel não encontrado.")
