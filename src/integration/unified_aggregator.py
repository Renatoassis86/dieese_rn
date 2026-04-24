import pandas as pd
import numpy as np
import os

class UnifiedAggregator:
    """Módulo 03: Integrador Unificado e Motor de Métricas Derivadas"""
    
    def __init__(self, input_dir="data/gold", pnad_results="pnad_sol/data/results/pnad_sol_indicadores_consolidados.csv"):
        self.input_dir = input_dir
        self.pnad_path = pnad_results
        self.output_dir = "data/gold/consolidated"
        os.makedirs(self.output_dir, exist_ok=True)

    def process(self):
        print("🚀 Iniciando Motor de Consolidação Exaustiva...")
        
        # 1. Carregando Bases
        df_territory = pd.read_csv("data/gold/territories/malha_territorial_rn.csv")
        df_pam = pd.read_csv("data/gold/agriculture/producao_agricola_pam_rn.csv")
        df_ppm = pd.read_csv("data/gold/agriculture/pecuaria_ppm_rn.csv")
        df_censo = pd.read_csv("data/gold/agriculture/agrofamiliar_censo_2017.csv")
        
        # 2. Processando Produção (PAM) - Criando Métricas de Eficiência
        # Pivotando PAM para ter Area e Valor lado a lado
        df_pam_pivot = df_pam.pivot_table(
            index=['cod_municipio', 'municipio', 'ano'], 
            columns='indicador', 
            values='valor'
        ).reset_index()
        
        # Limpeza de nomes e identificação dinâmica de colunas
        cols = df_pam_pivot.columns
        try:
            col_valor = [c for c in cols if 'Valor' in c or 'valor' in c.lower()][0]
            col_area = [c for c in cols if 'Área' in c or 'area' in c.lower()][0]
            
            # Metrica Derivada: Densidade Econômica (R$ por Hectare)
            df_pam_pivot['densidade_economica_rs_ha'] = (
                df_pam_pivot[col_valor] / df_pam_pivot[col_area].replace(0, np.nan)
            ).fillna(0)
            print(f"✔️ Métrica de Densidade Econômica calculada usando: {col_valor} / {col_area}")
        except IndexError:
            print("⚠️ Aviso: Colunas de Área ou Valor não encontradas no PAM. Métrica de densidade ignorada.")
        
        # 3. Processando Pecuária (PPM)
        df_ppm_pivot = df_ppm.pivot_table(
            index=['cod_municipio'], 
            columns='categoria', 
            values='valor'
        ).reset_index()
        df_ppm_pivot.columns = ['cod_municipio'] + [f"rebanho_{c.lower()}" for c in df_ppm_pivot.columns[1:]]

        # 4. Unificando Macroeconomia (PAM + PPM + Censo)
        df_macro = df_territory.merge(df_pam_pivot, on='cod_municipio', how='left')
        df_macro = df_macro.merge(df_ppm_pivot, on='cod_municipio', how='left')
        
        # Adicionando Agricultura Familiar do Censo
        df_censo_clean = df_censo[['cod_municipio', 'valor']].rename(columns={'valor': 'estabs_agro_familiar'})
        df_macro = df_macro.merge(df_censo_clean, on='cod_municipio', how='left')

        # 5. Integrando PNad (Dados Sociais)
        try:
            df_pnad = pd.read_csv(self.pnad_path)
            # Na PNAD o campo de localidade é 'local' (contém o nome da microrregião)
            df_final = df_macro.merge(df_pnad, left_on='microrregiao', right_on='local', how='left')
            
            # 6. Salvando Tabelas de Dimensão (FIXAS)
            # A. Tabela Geral para o Estudo Escrito (Agrupada por Microrregião)
            df_estudo = df_final.groupby(['mesorregiao', 'microrregiao']).agg({
                'Valor da produção': 'sum',
                'estabs_agro_familiar': 'sum',
                'taxa_informalidade': 'mean',
                'tx_vulnerabilidade_agro': 'mean'
            }).reset_index()
            df_estudo.to_csv(os.path.join(self.output_dir, "tabela_estudo_escrito_dimensoes.csv"), index=False, encoding='utf-8-sig')
            
            # B. Tabela Fixa para BI (Nível Município)
            df_final.to_csv(os.path.join(self.output_dir, "base_bi_observatorio_rural.csv"), index=False, encoding='utf-8-sig')

            print(f"✅ Consolidação Concluída!")
            print(f"📊 Arquivos gerados em: {self.output_dir}")
            
        except Exception as e:
            print(f"⚠️ Erro ao integrar PNAD (verifique se o arquivo existe): {e}")
            df_macro.to_csv(os.path.join(self.output_dir, "base_bi_macro_apenas.csv"), index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    agg = UnifiedAggregator()
    agg.process()
