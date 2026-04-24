import pandas as pd
import os

def get_sql(file_path, category):
    df = pd.read_csv(file_path)
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
    df['categoria'] = category
    df['municipio'] = df['municipio'].str.replace("'", "''")
    df['indicador'] = df['indicador'].str.replace("'", "''")
    
    sql = "INSERT INTO agro_indicadores (cod_municipio, municipio, ano, categoria, indicador, valor, unidade) VALUES "
    values = []
    for _, row in df.iterrows():
        val = f"('{row['cod_municipio']}', '{row['municipio']}', {row['ano']}, '{row['categoria']}', '{row['indicador']}', {row['valor']}, '{row['unidade']}')"
        values.append(val)
    
    return sql + ", ".join(values) + ";"

if __name__ == "__main__":
    base_path = "d:\\repositorio_geral\\app_dieese\\data\\gold\\agriculture"
    
    sql_censo = get_sql(os.path.join(base_path, "agrofamiliar_censo_2017.csv"), "Cenagro")
    sql_ppm = get_sql(os.path.join(base_path, "pecuaria_ppm_rn.csv"), "Pecuária")
    sql_pam = get_sql(os.path.join(base_path, "producao_agricola_pam_rn.csv"), "PAM")
    
    with open("insert_agro.sql", "w", encoding="utf-8") as f:
        f.write(sql_censo + "\n\n")
        f.write(sql_ppm + "\n\n")
        f.write(sql_pam + "\n\n")
    
    print("SQL gerado em insert_agro.sql")
