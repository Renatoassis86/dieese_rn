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
        'Valor pactuado': 'valor_pactuado',
        'Valor não executado': 'valor_nao_executado',
        '% de Execução': 'perc_execucao',
        'Status': 'status_recurso',
        'Origem do orçamento': 'origem_orcamento',
        'Público atendido': 'publico_atendido',
        'Nº do plano operacional': 'n_plano_operacional',
        'Vigência': 'vigencia',
        'paa_qtd_agricul_familiar_modal_compra_doacao_simul_i': 'mod_doacao_simultanea',
        'paa_qtd_agricul_familiar_modal_incentivo_leite_i': 'mod_incentivo_leite',
        'paa_qtd_agricul_familiar_modal_compra_direta_i': 'mod_compra_direta',
        'paa_qtd_agricul_familiar_modal_formacao_estoque_i': 'mod_formacao_estoque',
        'paa_qtd_agricul_familiar_modal_aquisicao_sementes_i': 'mod_aquisicao_sementes',
        'paa_indicador_adesao_municipio_i': 'indicador_adesao'
    }

    df = df.rename(columns=mapping)
    
    # Strictly keep onlymapped columns that exist in the DB
    valid_cols = list(mapping.values()) + ['municipio', 'territorio']
    existing_cols = [c for c in valid_cols if c in df.columns]
    df = df[existing_cols]

    # Manter só os municípios do Rio Grande do Norte (24)
    df['uf_code'] = df['codigo_ibge'].astype(str).str[:2]
    df = df[df['uf_code'] == '24']

    # Fill NaNs and cast types
    int_cols = ['ano', 'agricultores', 'mulheres', 'indicador_adesao']
    numeric_cols = [
        'valor_pago', 'valor_pactuado', 'valor_nao_executado', 'perc_execucao',
        'valor_doacao', 'valor_leite', 'quilos_alimentos', 'litros_leite',
        'mod_doacao_simultanea', 'mod_incentivo_leite', 'mod_compra_direta', 
        'mod_formacao_estoque', 'mod_aquisicao_sementes'
    ]
    
    # Calculate 'ano' from 'anomes_s' to ensure full series coverage
    df['anomes_s'] = df['anomes_s'].astype(str)
    df['ano'] = df['anomes_s'].str[:4].apply(lambda x: int(x) if x.isdigit() else 0)

    for c in int_cols:
        if c != 'ano': # already calculated
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)
            else:
                df[c] = 0
            
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        else:
            df[c] = 0.0
    
    # Replace any remaining Inf/-Inf/NaN across the whole dataframe
    df = df.fillna(0)

    # Handle UF derivation for historical rows missing sigla_uf
    def derive_uf(row):
        code = str(row['codigo_ibge'])
        if code.startswith('21'): return 'MA'
        if code.startswith('22'): return 'PI'
        if code.startswith('23'): return 'CE'
        if code.startswith('24'): return 'RN'
        if code.startswith('25'): return 'PB'
        if code.startswith('26'): return 'PE'
        if code.startswith('27'): return 'AL'
        if code.startswith('28'): return 'SE'
        if code.startswith('29'): return 'BA'
        current_uf = row.get('uf', '0')
        return current_uf if current_uf not in [0, '0', None] else '0'

    df['uf'] = df.apply(derive_uf, axis=1)

    # Drop temporary filtering column
    if 'uf_code' in df.columns: df = df.drop(columns=['uf_code'])

    print(f"📊 Mapeamento concluído. {len(df)} registros preparados.")
    
    batch_size = 500
    print(f"🚀 Ingerindo registros no Supabase em lotes de {batch_size}...")
    
    records = df.to_dict('records')
    for i in range(0, len(records), batch_size):
        if i % 5000 == 0: print(f"   -> Progresso: {i} / {len(records)}")
        batch = records[i:i+batch_size]
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }
        # Correct UPSERT syntax for PostgREST with multiple-column unique constraint
        url = f"{SUPABASE_URL}/rest/v1/paa_master?on_conflict=codigo_ibge,anomes_s"
        r = requests.post(url, headers=headers, json=batch)
        if r.status_code >= 400:
            print(f"   ❌ Erro no lote {i}: {r.text}")

    print("✅ Ingestão Master Concluída!")

if __name__ == "__main__":
    if os.path.exists(EXCEL_PATH):
        ingest_master()
    else:
        print("❌ Arquivo Excel não encontrado.")
