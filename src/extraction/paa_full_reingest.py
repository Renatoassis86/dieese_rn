import pandas as pd
import requests
import os
import json
from supabase import create_client, Client

# Configurações Supabase
SUPABASE_URL = "https://kyzcdpcmgiisllxmnhqn.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Resource ID Detalhado (MDS/SAGI)
RESOURCE_ID_PAA = "d86f9175-9e19-4809-b660-84c1f3cf7f45"

def fetch_detailed_paa():
    print(f"📥 Coletando dados detalhados do PAA (Resource: {RESOURCE_ID_PAA})...")
    url = "https://dados.gov.br/api/3/action/datastore_search"
    
    # Fazemos uma busca paginada para o RN
    all_records = []
    offset = 0
    batch_size = 5000
    
    while True:
        params = {
            "resource_id": RESOURCE_ID_PAA,
            "limit": batch_size,
            "offset": offset,
            "q": "RN"
        }
        
        try:
            r = requests.get(url, params=params, timeout=60, verify=False)
            r.raise_for_status()
            data = r.json()
            records = data.get("result", {}).get("records", [])
            
            if not records:
                break
            
            all_records.extend(records)
            print(f"   ✅ Coletados {len(all_records)} registros...")
            
            if len(records) < batch_size:
                break
            
            offset += batch_size
        except Exception as e:
            print(f"   ❌ Erro na coleta: {e}")
            break
            
    df = pd.DataFrame(all_records)
    # Filtrar rigorosamente por RN
    uf_cols = [c for c in df.columns if 'uf' in c.lower() or 'estado' in c.lower()]
    if uf_cols:
        df = df[df[uf_cols[0]].astype(str).str.upper() == 'RN']
        
    return df

def map_and_calculate(df):
    print("📈 Mapeando colunas e calculando indicadores derivados...")
    
    # Dicionário de Mapeamento (Ajustar Nomes Técnicos -> Supabase)
    # Baseado na inspeção visual das colunas mais comuns do MDS
    mapping = {
        'nu_ano': 'ano',
        'nu_mes': 'mes',
        'anomes_s': 'anomes_s',
        'codigo_ibge': 'codigo_ibge',
        'municipio': 'municipio',
        'nm_municipio': 'municipio',
        'vlr_pago': 'valor_pago',
        'vlr_executado': 'valor_pago',
        'vlr_pactual': 'valor_pactuado',
        'agricultores_familiares': 'agricultores',
        'agricultores': 'agricultores',
        'mulheres': 'mulheres',
        'qtd_alimentos_kg': 'quilos_alimentos',
        'qtd_leite_litros': 'litros_leite',
        'vlr_doacao_simultanea': 'mod_doacao_simultanea',
        'vlr_incentivo_leite': 'mod_incentivo_leite',
        'vlr_compra_direta': 'mod_compra_direta',
        'vlr_formacao_estoque': 'mod_formacao_estoque',
        'vlr_sementes': 'mod_aquisicao_sementes'
    }
    
    # Criar uma cópia com os nomes corretos
    final_cols = {}
    for old_col, new_col in mapping.items():
        if old_col in df.columns:
            final_cols[old_col] = new_col
            
    df_clean = df.rename(columns=final_cols)
    
    # Preencher colunas faltantes com 0
    required_cols = [
        'valor_pago', 'valor_pactuado', 'agricultores', 'mulheres', 
        'quilos_alimentos', 'litros_leite', 'mod_doacao_simultanea',
        'mod_incentivo_leite', 'mod_compra_direta', 'mod_formacao_estoque',
        'mod_aquisicao_sementes'
    ]
    for c in required_cols:
        if c not in df_clean.columns:
            df_clean[c] = 0
        df_clean[c] = pd.to_numeric(df_clean[c], errors='coerce').fillna(0)

    # CÁLCULOS DERIVADOS
    df_clean['ticket_medio'] = df_clean.apply(
        lambda row: row['valor_pago'] / row['agricultores'] if row['agricultores'] > 0 else 0, axis=1
    )
    df_clean['perc_feminino'] = df_clean.apply(
        lambda row: (row['mulheres'] / row['agricultores']) * 100 if row['agricultores'] > 0 else 0, axis=1
    )
    df_clean['valor_nao_executado'] = df_clean['valor_pactuado'] - df_clean['valor_pago']
    df_clean['perc_execucao'] = df_clean.apply(
        lambda row: (row['valor_pago'] / row['valor_pactuado']) * 100 if row['valor_pactuado'] > 0 else 0, axis=1
    )
    
    # Territorial mapping RN
    territorios = {
        'SERIDÓ': ['520550','520560','520330','520310'], # Exemplo Simplificado - Precisamos do Dicionário real
        # Automático via join se possível
    }
    
    return df_clean

def upload_to_supabase(df):
    print(f"🚀 Iniciando Upsert de {len(df)} registros para 'paa_master'...")
    
    # Converter para lista de dicts
    records = df.to_dict('records')
    
    # Lote de 500 para evitar erro de payload
    for i in range(0, len(records), 500):
        batch = records[i:i+500]
        try:
            supabase.table("paa_master").upsert(batch).execute()
            print(f"   📦 Lote {i//500 + 1} enviado.")
        except Exception as e:
            print(f"   ❌ Erro no lote {i//500 + 1}: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    raw_df = fetch_detailed_paa()
    if not raw_df.empty:
        processed_df = map_and_calculate(raw_df)
        upload_to_supabase(processed_df)
        print("🎉 Processo concluído com sucesso!")
    else:
        print("⚠️ Nenhum dado capturado para o RN.")
