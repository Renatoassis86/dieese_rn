import pandas as pd
import requests
import os

def extract_rn_municipalities():
    """
    Extracts the list of municipalities for Rio Grande do Norte (RN) from IBGE API.
    """
    print("Iniciando extração de municípios do RN via IBGE API...")
    
    # URL para municípios do RN (ID 24)
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/24/municipios"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Transformar em DataFrame com as colunas relevantes
        municipalities = []
        for item in data:
            municipalities.append({
                "codigo_ibge": str(item["id"]),
                "nome": item["nome"],
                "microrregiao": item["microrregiao"]["nome"],
                "mesorregiao": item["microrregiao"]["mesorregiao"]["nome"],
                "uf": "RN"
            })
            
        df = pd.DataFrame(municipalities)
        
        # Garantir diretório de saída
        output_path = "data/raw/municipios_rn.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Sucesso! {len(df)} municípios extraídos e salvos em: {output_path}")
        return df

    except Exception as e:
        print(f"Erro na extração: {e}")
        return None

if __name__ == "__main__":
    extract_rn_municipalities()
