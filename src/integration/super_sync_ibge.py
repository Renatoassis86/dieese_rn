import requests
import pandas as pd
import os

class TerritorialDeepSync:
    """Motor de Ingestão Territorial: Captura indicadores exaustivos no nível de Microrregião (N9)"""
    
    BASE_URL = "https://servicodados.ibge.gov.br/api/v3/agregados"

    def __init__(self, output_dir="data/gold/agriculture_deep"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def fetch_territorial(self, table_id, variables, filter_str, label):
        print(f"🌍 Extraindo Dimensão {label} para Microrregiões do RN...")
        # Usando N9[all] para Microrregiões, filtrando depois para o estado 24
        endpoint = f"{self.BASE_URL}/{table_id}/periodos/2017/variaveis/{variables}?localidades=N9[all]&classificacao={filter_str}"
        
        try:
            response = requests.get(endpoint, timeout=40)
            response.raise_for_status()
            data = response.json()
            
            rows = []
            for var_data in data:
                var_name = var_data.get('variavel', '')
                for result in var_data.get('resultados', []):
                    category = " | ".join([c.get('resumo', '') for c in result.get('classificacoes', [])])
                    for series in result.get('series', []):
                        # Filtrando apenas microrregiões do RN (Códigos começam com 24)
                        if series['localidade']['id'].startswith('24'):
                            rows.append({
                                "id_territorio": series['localidade']['id'],
                                "nome_territorio": series['localidade']['nome'],
                                "dimensao": label,
                                "categoria": category,
                                "indicador": var_name,
                                "valor": list(series['serie'].values())[0]
                            })
            return rows
        except Exception as e:
            print(f"❌ Falha em {label}: {e}")
            return []

    def run(self):
        all_data = []
        
        # 1. Gênero e Gestão
        all_data.extend(self.fetch_territorial("6778", "183", "829[46304]|2[4]", "GENERO_MULHER"))
        
        # 2. Sucessão Rural (Juventude < 35 anos)
        # C777 (Idade do produtor): 46294 (Menos de 25), 46295 (25 a 35)
        all_data.extend(self.fetch_territorial("6777", "183", "829[46304]|777[46294,46295]", "JUVENTUDE_SUCESSÃO"))
        
        # 3. Orientação Técnica (ATER)
        all_data.extend(self.fetch_territorial("6779", "183", "829[46304]|12515[3011]", "ATER_COBERTURA"))
        
        # 4. Uso de Internet (Tecnologia)
        all_data.extend(self.fetch_territorial("6783", "183", "829[46304]|12514[3011]", "INTERNET_RURAL"))

        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(os.path.join(self.output_dir, "censo_agro_microrregioes_final.csv"), index=False, encoding='utf-8-sig')
            print(f"✅ Sincronização Territorial Concluída! {len(df)} indicadores regionais capturados.")
        else:
            print("❌ Erro: Nenhuma microrregião capturada.")

if __name__ == "__main__":
    sync = TerritorialDeepSync()
    sync.run()
