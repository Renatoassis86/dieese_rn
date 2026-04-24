import requests
import pandas as pd
import os
import time

class AgricultureSync:
    """Módulo 02 do Motor: Extração de Dados de Produção e Agricultura Familiar (SIDRA)"""
    
    BASE_URL = "https://servicodados.ibge.gov.br/api/v3/agregados"

    def __init__(self, output_dir="data/gold/agriculture"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def fetch_sidra_table(self, table_id, variables, label):
        """Busca dados de uma tabela SIDRA para todos os municípios do RN"""
        print(f"🌾 Extraindo {label} (Tabela {table_id})...")
        
        # Parâmetro N6[N3[24]] foca em todos os municípios (N6) do estado 24 (RN)
        # Puxamos o último período disponível (last)
        endpoint = f"{self.BASE_URL}/{table_id}/periodos/last/variaveis/{variables}?localidades=N6[N3[24]]"
        
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()
            
            extracted_rows = []
            if not data:
                print(f"⚠️ Nenhum dado retornado para a tabela {table_id}")
                return
                
            for var_data in data:
                var_name = var_data.get('variavel', 'Indicador')
                unit = var_data.get('unidade', '')
                for result in var_data.get('resultados', []):
                    # Tenta pegar o nome da categoria/produto se existir
                    category = "Geral"
                    if result.get('classificacoes'):
                        category = result['classificacoes'][0].get('resumo', 'Geral')
                    
                    for series in result.get('series', []):
                        mun_id = series['localidade']['id']
                        mun_nome = series['localidade']['nome']
                        for period, value in series['serie'].items():
                            extracted_rows.append({
                                "cod_municipio": mun_id,
                                "municipio": mun_nome,
                                "ano": period,
                                "categoria": category,
                                "indicador": var_name,
                                "valor": value,
                                "unidade": unit
                            })
            
            df = pd.DataFrame(extracted_rows)
            # Limpeza básica (converter para numérico)
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
            
            filename = f"{label.lower().replace(' ', '_')}_rn.csv"
            output_path = os.path.join(self.output_dir, filename)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            print(f"✅ {label} salvo com sucesso! ({len(df)} registros)")
            return df

        except Exception as e:
            print(f"❌ Erro ao extrair {label}: {e}")
            return None

    def fetch_censo_agro_familiar(self):
        """Busca dados específicos do Censo Agro 2017 com TODOS os IDs de classificação obrigatórios (IDs validados)"""
        print("🌾 Tentativa Deep Query: Extraindo Agricultura Familiar (Censo 2017 - Tabela 6778)...")
        
        # Tabela 6778 exige 6 classificações para evitar ambiguidade (IDs extraídos do metadado)
        filters = (
            "829[46304]|"    # Agricultura familiar - sim
            "309[10969]|"    # Existência de energia elétrica - Total
            "218[46502]|"    # Condição do produtor - Total
            "12553[46523]|"  # Residência do produtor - Total
            "12517[113601]|" # Grupos de atividade - Total
            "220[110085]"    # Grupos de área total - Total
        )
        
        endpoint = f"{self.BASE_URL}/6778/periodos/2017/variaveis/183?localidades=N6[N3[24]]&classificacao={filters}"
        
        return self.fetch_sidra_table_raw(endpoint, "AgroFamiliar_Censo_2017")

    def fetch_sidra_table_raw(self, url, label):
        """Método auxiliar para chamadas com URLs complexas/pré-formatadas"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            extracted_rows = []
            for var_data in data:
                var_name = var_data.get('variavel', 'Indicador')
                unit = var_data.get('unidade', '')
                for result in var_data.get('resultados', []):
                    category = "Geral"
                    if result.get('classificacoes'):
                        category = " | ".join([c.get('resumo', '') for c in result['classificacoes']])
                    
                    for series in result.get('series', []):
                        extracted_rows.append({
                            "cod_municipio": series['localidade']['id'],
                            "municipio": series['localidade']['nome'],
                            "ano": list(series['serie'].keys())[0],
                            "categoria": category,
                            "indicador": var_name,
                            "valor": list(series['serie'].values())[0],
                            "unidade": unit
                        })
            
            df = pd.DataFrame(extracted_rows)
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
            output_path = os.path.join(self.output_dir, f"{label.lower()}.csv")
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"✅ {label} salvo com sucesso! ({len(df)} registros)")
            return df
        except Exception as e:
            print(f"❌ Erro ao extrair {label}: {e}")
            return None

    def run_sync(self):
        """Executa a sincronização de todas as tabelas macro de agricultura"""
        # 1. PAM - Produção Agrícola
        self.fetch_sidra_table("1612", "214|215", "Producao_Agricola_PAM")
        
        # 2. PPM - Pecuária
        self.fetch_sidra_table("3939", "105", "Pecuaria_PPM")
        
        # 3. Censo Agro 2017 (Tentativa com parâmetros obrigatórios)
        self.fetch_censo_agro_familiar()
        
        print("\n🚀 Módulo 02 finalizado. Dados macro disponíveis em data/gold/agriculture/")

if __name__ == "__main__":
    sync = AgricultureSync()
    sync.run_sync()
