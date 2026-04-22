import pandas as pd
import requests
import os
from supabase import create_client
from dotenv import load_dotenv
import time

# Configurações
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

PNAE_URLS = {
    2022: "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/pnae/consultas/dados-agricultura-familiar-planilhas/Planilha2022_04_3_24.xlsx/@@download/file/Planilha2022_04_3_24.xlsx",
    2021: "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/pnae/consultas/dados-agricultura-familiar-planilhas/Planilha2021_04_3_24.xlsx/@@download/file/Planilha2021_04_3_24.xlsx",
    2020: "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/pnae/consultas/dados-agricultura-familiar-planilhas/Planilha2020_04_3_24.xlsx/@@download/file/Planilha2020_04_3_24.xlsx"
}

def download_file(url, year):
    path = f"outputs/pnae_raw_{year}.xlsx"
    if os.path.exists(path):
        return path
    print(f"📥 Baixando PNAE {year}...")
    response = requests.get(url)
    with open(path, 'wb') as f:
        f.write(response.content)
    return path

def ingest_pnae():
    all_data = []
    
    for year, url in PNAE_URLS.items():
        file_path = download_file(url, year)
        print(f"📖 Processando PNAE {year}...")
        
        # FNDE spreadshets sometimes have title headers in first rows.
        # Let's try to detect the header row by searching for 'UF'
        raw_df = pd.read_excel(file_path)
        header_row = 0
        for i, row in raw_df.iterrows():
            row_vals = [str(x).upper() for x in row.values]
            if 'UF' in row_vals or 'S_SIGLA_UF' in row_vals or 'SIGLA_UF' in row_vals:
                header_row = i + 1
                break
        
        print(f"   🎯 Cabeçalho detectado na linha {header_row}")
        df = pd.read_excel(file_path, skiprows=header_row)
        
        # Se o header_row for 0, talvez o primeiro read_excel já pegou.
        if header_row == 0:
            df = raw_df
            
        # Filtrar Nordeste e RN (simplificado para demonstração inicial via UF)
        # Colunas típicas: 'ANO_EXERCICIO', 'UF', 'CODIGO_IBGE', 'NOME_ENTIDADE_EXECUTORA', 'VALOR_TOTAL_REPASSADO', 'VALOR_AQUISICAO_AF'
        
        # Normalizar colunas (FNDE muda os headers às vezes)
        df.columns = [str(c).strip().upper() for c in df.columns]
        print(f"   🔍 Colunas encontradas em {year}: {list(df.columns)[:10]}...")
        
        mapping = {
            'ANO': 'ano',
            'ANO_EXERCICIO': 'ano',
            'S_ANO_REFERENCIA': 'ano',
            'UF': 'uf',
            'SIGLA_UF': 'uf',
            'S_SIGLA_UF': 'uf',
            'IBGE': 'codigo_ibge',
            'CODIGO_IBGE': 'codigo_ibge',
            'CO_MUNICIPIO_IBGE': 'codigo_ibge',
            'CO_IBGE': 'codigo_ibge',
            'CD_MUNICIPIO': 'codigo_ibge',
            'COD_IBGE': 'codigo_ibge',
            'ENTIDADE EXECUTORA': 'entidade_executora',
            'NOME_ENTIDADE_EXECUTORA': 'entidade_executora',
            'NO_ENTIDADE': 'entidade_executora',
            'VALOR TRANSFERIDO': 'valor_total_repassado',
            'VALOR_TOTAL_REPASSADO': 'valor_total_repassado',
            'VL_REPASSE_TOTAL_FNDE': 'valor_total_repassado',
            'VALOR AQUISIÇÕES DA AGRICULTURA FAMILIAR': 'valor_aquisicao_af',
            'VALOR_AQUISICAO_AF': 'valor_aquisicao_af',
            'VL_TOTAL_AF': 'valor_aquisicao_af',
            'PERCENTUAL': 'percentual_af',
            'PERCENTUAL_AF': 'percentual_af',
            'PC_TOTAL_AF': 'percentual_af',
            '%_AF': 'percentual_af'
        }
        
        df = df.rename(columns=mapping)
        
        # Filtro Nordeste
        if 'uf' in df.columns:
            df = df[df['uf'].isin(['MA', 'PI', 'CE', 'RN', 'PB', 'PE', 'AL', 'SE', 'BA'])]
        
        # Manter apenas as colunas desejadas que existem no df
        valid_cols = list(set(mapping.values()))
        df = df[[c for c in valid_cols if c in df.columns]]
        
        # ELIMINAR LINHAS SEM CÓDIGO IBGE (Rodapés, Vazios)
        df = df.dropna(subset=['codigo_ibge'])
        
        # Garantir types
        df['ano'] = year
        df['codigo_ibge'] = df['codigo_ibge'].astype(str).str.split('.').str[0] # Remover .0 de floats
        
        if 'valor_total_repassado' in df.columns:
            df['valor_total_repassado'] = pd.to_numeric(df['valor_total_repassado'], errors='coerce').fillna(0)
        if 'valor_aquisicao_af' in df.columns:
            df['valor_aquisicao_af'] = pd.to_numeric(df['valor_aquisicao_af'], errors='coerce').fillna(0)
        if 'percentual_af' in df.columns:
            # Em alguns anos, o percentual vem como '35,40' (string) ou float
            df['percentual_af'] = df['percentual_af'].astype(str).str.replace(',', '.')
            df['percentual_af'] = pd.to_numeric(df['percentual_af'], errors='coerce').fillna(0)
            
        all_data.append(df)
        
    final_df = pd.concat(all_data)
    records = final_df.to_dict('records')
    
    print(f"🚀 Ingerindo {len(records)} registros no Supabase...")
    batch_size = 500
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        supabase.table("pnae_master").insert(batch).execute()
        print(f"   -> Progresso: {i+len(batch)} / {len(records)}")

if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    ingest_pnae()
