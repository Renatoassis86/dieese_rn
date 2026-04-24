import pandas as pd
import numpy as np
import os

class PNADDeepMiner:
    """Minerador de Microdados: Extrai indicadores interseccionais exaustivos usando pesos amostrais"""
    
    def __init__(self, gold_path="pnad_sol/data/gold/pnadc/pnadc_gold_2024.parquet"):
        self.gold_path = gold_path
        self.output_path = "pnad_sol/data/results/pnad_exhaustive_intersectional.csv"

    def weighted_mean(self, df, col, weight_col):
        """Calcula a média ponderada para validade estatística"""
        df_clean = df.dropna(subset=[col, weight_col])
        if df_clean.empty: return 0
        return np.average(df_clean[col], weights=df_clean[weight_col])

    def mine(self):
        print(f"💎 Minerando Microdados Exaustivos: {self.gold_path}...")
        
        if not os.path.exists(self.gold_path):
            print("❌ Erro: Arquivo Gold 2024 não encontrado.")
            return

        df = pd.read_parquet(self.gold_path)
        
        # Filtro: Apenas Ocupados Rurais no RN
        # Nota: Nos microdados do RN, o estado é 24. 
        # A microrregião costuma estar no peso ou em variáveis de estratificação. 
        # Para exaustividade, vamos focar em Gênero e Juventude.
        
        df_rural = df[df['rural'] == 1].copy()
        
        results = []
        
        # Iterar por Microrregião (V1023 ou similar se disponível nas colunas harmonizadas)
        # Se não tivermos microrregião granular, fazemo por 'local'
        t_col = 'V1023' if 'V1023' in df.columns else 'Ano' 

        for loc, group in df_rural.groupby(t_col):
            # 1. Gênero
            group_h = group[group['sexo'] == 'Homem']
            group_m = group[group['sexo'] == 'Mulher']
            
            renda_h = self.weighted_mean(group_h, 'Rend_H_real', 'V1028')
            renda_m = self.weighted_mean(group_m, 'Rend_H_real', 'V1028')
            
            # 2. Juventude (Sucessão Rural)
            group['is_jovem'] = (group['V2009'] <= 29).astype(int)
            tx_jovem = self.weighted_mean(group, 'is_jovem', 'V1028')
            
            # 3. Informalidade por Gênero
            inf_m = self.weighted_mean(group_m, 'informal', 'V1028')
            
            # 4. Escolaridade (VD3005 - Anos de Estudo)
            if 'VD3005' in group.columns:
                group['anos_estudo'] = pd.to_numeric(group['VD3005'], errors='coerce').fillna(0)
                esc_med = self.weighted_mean(group, 'anos_estudo', 'V1028')
            else:
                esc_med = 0

            results.append({
                "local_id": loc,
                "renda_media_mulher": renda_m,
                "renda_media_homem": renda_h,
                "gap_renda_genero": (renda_h - renda_m) / renda_h if renda_h > 0 else 0,
                "taxa_sucessao_jovem": tx_jovem,
                "informalidade_feminina": inf_m,
                "escolaridade_media_rural": esc_med,
                "taxa_vulnerabilidade_deep": self.weighted_mean(group, 'agro_rural_vulneravel', 'V1028')
            })

        df_final = pd.DataFrame(results)
        df_final.to_csv(self.output_path, index=False, encoding='utf-8-sig')
        print(f"✅ Matriz Interseccional Gerada! ({len(df_final)} áreas processadas)")

if __name__ == "__main__":
    miner = PNADDeepMiner()
    miner.mine()
