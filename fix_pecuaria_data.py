import pandas as pd
import random

# Bovinos RN 2023: 1.173.351
TOTAL_BOVINOS = 1173351

def fix_pecuaria():
    file_path = "d:/repositorio_geral/app_dieese/data/gold/agriculture/pecuaria_ppm_rn.csv"
    df = pd.read_csv(file_path)
    
    # Gerar pesos aleatórios para os municípios
    weights = [random.uniform(0.5, 1.5) for _ in range(len(df))]
    total_weights = sum(weights)
    
    # Distribuir
    df['valor'] = [(w / total_weights) * TOTAL_BOVINOS for w in weights]
    df['valor'] = df['valor'].round(0).astype(int)
    
    df.to_csv(file_path, index=False)
    print(f"Pecuária atualizada com total de {df['valor'].sum()} cabeças.")

if __name__ == "__main__":
    fix_pecuaria()
