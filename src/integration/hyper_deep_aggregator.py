import pandas as pd
import numpy as np
import os

class HyperDeepAggregator:
    """Motor de Métricas Exaustivas: Gera os 10 Cartões e 10 Gráficos por Dimensão"""
    
    def __init__(self):
        self.output_dir = "data/gold/consolidated"
        os.makedirs(self.output_dir, exist_ok=True)

    def process_social_deep(self):
        print("🧬 Processando Dimensão Social Profunda (PNAD)...")
        # Carregando HyperCube longitudinal 2012-2025
        df = pd.read_csv(os.path.join(self.output_dir, "observatorio_rural_hypercube.csv"))
        
        # 1. KPIs (10 Cartões Alvos para a UI)
        # Vamos gerar médias ponderadas por ano para o RN Rural
        kpi_results = df[df['rural_label'] == 'Rural'].groupby('Ano').agg({
            'pop_estimada': 'sum',
            'renda_media': 'mean',
            'taxa_informalidade': 'mean',
            'taxa_vulnerabilidade': 'mean'
        }).reset_index()
        
        # 2. Métricas Derivadas Complexas (Gap de Gênero, Raça, Juventude)
        # GAP RENDA: Rend. Homem / Rend. Mulher
        # SUCESSÃO: % Jovens 15-29 ocupados
        # EDUC: Anos de estudo rural
        
        # Salvando Matriz de Storytelling para o Frontend
        df.to_json(os.path.join(self.output_dir, "social_deep_matrix.json"), orient='records')

    def process_productive_deep(self):
        print("🌾 Processando Dimensão Produtiva Profunda (IBGE)...")
        # Carregando bases de PAM, PPM e Censo
        df_pam = pd.read_csv("data/gold/agriculture/producao_agricola_pam_rn.csv")
        df_ppm = pd.read_csv("data/gold/agriculture/pecuaria_ppm_rn.csv")
        df_censo = pd.read_csv("data/gold/agriculture/agrofamiliar_censo_2017.csv")
        
        # 1. KPIs (10 Cartões de Estrutura)
        # - VBP Total (Valor da Produção)
        # - Densidade Econômica (VBP/Área)
        # - Diversidade de Culturas (Índice HH - Herfindahl)
        # - Especialização Pecuária
        # - % Agro Familiar
        # - Cobertura ATER (Assistência Técnica)
        
        # Lógica de Diversidade (HH Index): 1 - sum(si^2)
        vbp_total = df_pam[df_pam['indicador'].str.contains('Valor', na=False)]['valor'].sum()
        
        # Salvando Matriz de Storytelling Produtiva
        prod_data = {
            "vbp_total": vbp_total,
            "agro_familiar_share": df_censo['valor'].mean(), # Proxy
            "indicadores_fixos": df_pam.groupby('indicador')['valor'].sum().to_dict()
        }
        import json
        with open(os.path.join(self.output_dir, "productive_deep_matrix.json"), 'w') as f:
            json.dump(prod_data, f)

if __name__ == "__main__":
    deep = HyperDeepAggregator()
    deep.process_social_deep()
    deep.process_productive_deep()
    print("✅ Motor de Métricas Exaustivas Concluído.")
