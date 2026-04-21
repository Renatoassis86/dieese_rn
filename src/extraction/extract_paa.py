import pandas as pd
import requests
import os
import json

def extract_paa_data(resource_id):
    """
    Extracts PAA data from dados.gov.br CKAN API using the Datastore search.
    """
    print(f"Iniciando extração do PAA via API (Resource ID: {resource_id})...")
    
    base_url = "https://dados.gov.br/api/3/action/datastore_search"
    
    # Parâmetros para buscar dados do RN
    # Nota: Filtramos por 'sigla_uf' ou similar dependendo da estrutura do recurso
    params = {
        "resource_id": resource_id,
        "limit": 5000,
        "q": "RN" # Busca geral por RN para garantir captura
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        # Tenta a extração
        response = requests.get(base_url, params=params, headers=headers, verify=False)
        
        if response.status_code == 401:
            print("Erro 401: A API do dados.gov.br está bloqueando o acesso automatizado no momento.")
            print("DICA: Tente baixar o CSV manualmente no portal e salve em data/raw/paa_rn.csv")
            return None
            
        response.raise_for_status()
        data = response.json()
        
        records = data.get("result", {}).get("records", [])
        if not records:
            print("Nenhum registro encontrado para o filtro aplicado.")
            return None
            
        df = pd.DataFrame(records)
        
        # Filtragem adicional para garantir que é RN (caso a busca 'q' tenha sido ampla)
        # Adaptar os nomes das colunas conforme o dicionário encontrado
        cols = df.columns.tolist()
        uf_col = next((c for c in cols if 'uf' in c.lower() or 'estado' in c.lower()), None)
        
        if uf_col:
            df = df[df[uf_col].astype(str).str.upper() == 'RN']
            
        # Salvar dados
        output_path = "data/raw/paa_rn_extracted.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print(f"Sucesso! {len(df)} registros do PAA extraídos para o RN.")
        print(f"Dados salvos em: {output_path}")
        return df

    except Exception as e:
        print(f"Erro na extração via API: {e}")
        return None

def validate_against_studies(df_paa):
    """
    Placeholder para validação cruzada com os documentos na pasta docs.
    """
    if df_paa is None:
        return
        
    print("\nIniciando validação preliminar...")
    # Exemplo: Comparar total de recursos ou agricultores se houver coluna correspondente
    # No Ceará (Estudo 2019), vimos que em 2015 o total foi R$ 12.7M
    # Aqui buscaremos os valores para o RN se disponíveis
    
    summary = df_paa.describe()
    print("Resumo estatístico da extração:")
    print(summary)
    
    # Verificar se as variáveis do dicionário (paa_indicador_adesao_municipio_i, etc) estão presentes
    vars_found = [v for v in df_paa.columns if 'paa' in v.lower()]
    print(f"Variáveis técnicas encontradas: {vars_found}")

if __name__ == "__main__":
    # Resource IDs comuns para PAA (precisam ser validados no portal dados.gov.br)
    # Exemplo mockado baseado na estrutura do MDS/SAGI
    RESOURCE_ID_EXECUCAO = "paa-execucao-geral-placeholder" # Substituir pelo ID real do portal
    
    # Desabilita avisos de SSL se necessário para o ambiente gov.br
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    df = extract_paa_data(RESOURCE_ID_EXECUCAO)
    validate_against_studies(df)
