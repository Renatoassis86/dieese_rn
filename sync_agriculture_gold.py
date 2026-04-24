import pandas as pd
import os
from supabase import create_client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def sync_file(file_path, category):
    print(f"Sincronizando {file_path}...")
    df = pd.read_csv(file_path)
    
    # Limpeza básica
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
    df['categoria'] = category
    
    # Preparar para o Supabase
    records = df.to_dict('records')
    
    # Criar tabela se não existir (via execute_sql se necessário, mas aqui assumimos que existe ou usamos a API)
    # Para simplificar, vamos inserir em blocos de 1000
    for i in range(0, len(records), 1000):
        batch = records[i:i+1000]
        try:
            supabase.table("agro_indicadores").upsert(batch).execute()
        except Exception as e:
            print(f"Erro no batch {i}: {e}")

if __name__ == "__main__":
    # Garantir que a tabela existe
    # SQL: CREATE TABLE IF NOT EXISTS agro_indicadores (cod_municipio text, municipio text, ano int, categoria text, indicador text, valor float, unidade text);
    
    base_path = "d:\\repositorio_geral\\app_dieese\\data\\gold\\agriculture"
    
    sync_file(os.path.join(base_path, "agrofamiliar_censo_2017.csv"), "Cenagro")
    sync_file(os.path.join(base_path, "pecuaria_ppm_rn.csv"), "Pecuária")
    sync_file(os.path.join(base_path, "producao_agricola_pam_rn.csv"), "PAM")
    
    print("Sincronização concluída!")
