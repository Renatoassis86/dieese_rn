import requests
import pandas as pd
import os

class TerritorySync:
    """Módulo 01 do Motor: Sincronização de Malha Territorial via API IBGE"""
    
    API_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/24/municipios"

    def __init__(self, output_dir="data/gold/territories"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def fetch_official_hierarchy(self):
        """Busca a hierarquia completa do RN direto da API"""
        print("🔍 Consultando API de Localidades do IBGE (Estado 24 - RN)...")
        
        try:
            response = requests.get(self.API_URL)
            response.raise_for_status()
            municipios = response.json()
            
            flat_data = []
            for m in municipios:
                flat_data.append({
                    "cod_municipio": m['id'],
                    "municipio": m['nome'],
                    "cod_micro": m['microrregiao']['id'],
                    "microrregiao": m['microrregiao']['nome'],
                    "cod_meso": m['microrregiao']['mesorregiao']['id'],
                    "mesorregiao": m['microrregiao']['mesorregiao']['nome']
                })
            
            df = pd.DataFrame(flat_data)
            output_path = os.path.join(self.output_dir, "malha_territorial_rn.csv")
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            print(f"✅ Sincronização Territorial Concluída!")
            print(f"📍 {len(df)} municípios mapeados em {df['microrregiao'].nunique()} microrregiões.")
            print(f"📦 Arquivo gerado: {output_path}")
            
            return df

        except Exception as e:
            print(f"❌ Falha crítica no Motor Territorial: {e}")
            return None

if __name__ == "__main__":
    sync = TerritorySync()
    sync.fetch_official_hierarchy()
