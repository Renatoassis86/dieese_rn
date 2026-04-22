import pandas as pd
import requests
import json
import os

# Configurações do Supabase (obtidas do .env)
SUPABASE_URL = "https://kyzcdpcmgiisllxmnhqn.supabase.co"
# Nota: Usando a SERVICE_ROLE_KEY se disponível, ou a anon se não houver restrições.
# Descobri que a chave no .env é a publishable/anon. 
# Para ingestão massiva, vou usar a API REST do Supabase.
SUPABASE_KEY = "sb_publishable_DRWOVTb1-KWvTd35C_E18A_-L9RQtUJ" 

def ingest_data():
    print("⏳ Lendo dados para ingestão...")
    file_path = "outputs/paa_reports/PAA_OBSERVATORIO_FINAL_MASTER.xlsx"
    
    # Lendo o nível municipal que contém todos os dados
    df = pd.read_excel(file_path, sheet_name="4. RN Municipal")
    
    # Mapeamento de colunas para o banco
    # Nomes das colunas no Excel gerado: Município, Território, Ano, recur_pagos_agricul_paa_f, agricultores_fornec_paa_i, paa_qtd_agricul_familiar_sexo_feminino_i, paa_vlr_pago_exec_incentivo_leite_d
    
    # Limpeza
    df = df.rename(columns={
        'Município': 'municipio',
        'Território': 'territorio',
        'Ano': 'ano',
        'recur_pagos_agricul_paa_f': 'valor_pago',
        'agricultores_fornec_paa_i': 'agricultores',
        'paa_qtd_agricul_familiar_sexo_feminino_i': 'mulheres',
        'paa_vlr_pago_exec_incentivo_leite_d': 'valor_leite'
    })
    
    df['uf'] = 'RN'
    # Adicionando valor_doacao (estimado ou zero por enquanto se não tiver na municipal)
    df['valor_doacao'] = 0 
    
    # Converter para JSON para o Supabase
    records = df.to_dict('records')
    
    print(f"🚀 Enviando {len(records)} registros para o banco de dados...")
    
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
        if r.status_code not in [200, 201]:
            print(f"❌ Erro no lote {i}: {r.text}")
        else:
            print(f"✅ Lote {i} enviado com sucesso.")

if __name__ == "__main__":
    ingest_data()
