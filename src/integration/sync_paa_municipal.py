"""
Extraction and Integration Fix: MiSocial API -> Supabase (RN Municipal PAA)
Fixes integer casting for qtd_beneficiados and handles errors better.
"""
import pandas as pd
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

FIELD_MAP = {
    'codigo_ibge': 'cod_municipio_ibge',
    'sigla_uf': 'sigla_uf',
    'municipio': 'nome_municipio',
    'recur_pagos_agricul_paa_f': 'val_executado',
    'agricultores_fornec_paa_i': 'qtd_beneficiados'
}

def extract_paa_year(year):
    print(f"📡 Extraindo PAA {year} (RN) via MiSocial API...")
    url = "https://aplicacoes.mds.gov.br/sagi/servicos/misocial/"
    fields = "codigo_ibge,anomes_s,sigla_uf,municipio,recur_pagos_agricul_paa_f,agricultores_fornec_paa_i"
    params = {
        "fl": fields,
        "fq": [f"anomes_s:{year}*", "sigla_uf:RN"],
        "q": "*:*",
        "rows": 100000,
        "wt": "json"
    }

    try:
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        if not docs: return None
        return pd.DataFrame(docs)
    except Exception as e:
        print(f"❌ Erro ao extrair {year}: {e}")
        return None

def sync_to_supabase(df):
    if df is None: return
    print(f"🚀 Sincronizando {len(df)} registros com Supabase...")
    
    df['ano'] = df['anomes_s'].astype(str).str[:4].astype(int)
    df['mes'] = df['anomes_s'].astype(str).str[4:].astype(int)
    df = df.rename(columns=FIELD_MAP)
    
    # Proper casting
    df['val_executado'] = pd.to_numeric(df['val_executado'], errors='coerce').fillna(0).astype(float)
    # Convert Beneficiarios to Float FIRST to handle "0.0", then Int
    df['qtd_beneficiados'] = pd.to_numeric(df['qtd_beneficiados'], errors='coerce').fillna(0).astype(float).astype(int)
    
    final_cols = ['ano', 'mes', 'sigla_uf', 'cod_municipio_ibge', 'nome_municipio', 'val_executado', 'qtd_beneficiados']
    data_to_save = df[final_cols].to_dict(orient='records')
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    api_url = f"{SUPABASE_URL}/rest/v1/paa_dados"
    
    # Clear old data before reload for cleanliness (Optional, but good for RN)
    requests.delete(api_url, headers=headers, params={"sigla_uf": "eq.RN"})

    chunk_size = 1000
    for i in range(0, len(data_to_save), chunk_size):
        chunk = data_to_save[i:i+chunk_size]
        res = requests.post(api_url, headers=headers, json=chunk)
        if res.status_code not in [200, 201]:
            print(f"❌ Erro no lote {i}: {res.text}")
        else:
            print(f"✔️ Lote {i} enviado ({len(chunk)} rows).")

if __name__ == "__main__":
    years = [2021, 2022, 2023, 2024, 2025]
    all_data = []
    for y in years:
        df_y = extract_paa_year(y)
        if df_y is not None: all_data.append(df_y)
            
    if all_data:
        sync_to_supabase(pd.concat(all_data))
        print("🎉 Integração RN concluída!")
