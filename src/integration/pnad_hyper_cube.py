import pandas as pd
import numpy as np
import os
import glob

class PNADHyperCube:
    """Motor de Cubo de Dados: Cria uma matriz exaustiva de indicadores 2012-2025"""
    
    def __init__(self, gold_dir="pnad_sol/data/gold/pnadc"):
        self.gold_dir = gold_dir
        self.output_path = "data/gold/consolidated/observatorio_rural_hypercube.csv"
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    def calculate_cube(self, df, ano):
        # Filtro: Apenas RN (UF 24)
        df_rn = df[df['UF'] == "24"].copy()
        
        # Conversão de tipos e tratamentos
        df_rn['V2009'] = pd.to_numeric(df_rn['V2009'], errors='coerce')
        df_rn['faixa_etaria'] = pd.cut(df_rn['V2009'], bins=[0, 14, 29, 59, 120], labels=['Crianca', 'Jovem', 'Adulto', 'Idoso'])
        df_rn['sexo'] = df_rn['sexo'].fillna('Desconhecido')
        df_rn['rural_label'] = df_rn['rural'].map({1: "Rural", 0: "Urbano"})
        
        # DEFINIÇÃO DO CUBO: Cruzamento Exaustivo
        group_cols = ['Ano', 'rural_label', 'sexo', 'faixa_etaria', 'ees_tipo_unidade']
        
        # Métricas Agregadas Ponderadas (Simplificado para o Python via .multiply)
        df_rn['renda_ponderada'] = df_rn['Rend_H_real'] * df_rn['V1028']
        df_rn['informal_ponderado'] = df_rn['informal'] * df_rn['V1028']
        df_rn['vulneravel_ponderado'] = df_rn['agro_rural_vulneravel'] * df_rn['V1028']
        
        cube = df_rn.groupby(group_cols).agg(
            n_amostral=('V1028', 'count'),
            pop_estimada=('V1028', 'sum'),
            renda_total=('renda_ponderada', 'sum'),
            informal_total=('informal_ponderado', 'sum'),
            vulneraveis_total=('vulneravel_ponderado', 'sum')
        ).reset_index()
        
        # Cálculo das Taxas Finais
        cube['renda_media'] = cube['renda_total'] / cube['pop_estimada']
        cube['taxa_informalidade'] = cube['informal_total'] / cube['pop_estimada']
        cube['taxa_vulnerabilidade'] = cube['vulneraveis_total'] / cube['pop_estimada']
        
        return cube

    def process_all_years(self):
        print("🧊 Iniciando construção do HyperCube (2012-2025)...")
        files = glob.glob(os.path.join(self.gold_dir, "*.parquet"))
        all_cubes = []
        
        for f in sorted(files):
            ano = os.path.basename(f).split('_')[-1].replace('.parquet', '')
            print(f"   -> Processando {ano}...")
            df_year = pd.read_parquet(f)
            all_cubes.append(self.calculate_cube(df_year, ano))
        
        final_cube = pd.concat(all_cubes, ignore_index=True)
        final_cube.to_csv(self.output_path, index=False, encoding='utf-8-sig')
        print(f"✅ HyperCube Exaustivo finalizado: {self.output_path}")

if __name__ == "__main__":
    miner = PNADHyperCube()
    miner.process_all_years()
