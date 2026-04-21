import pandas as pd
import requests
import os

def run_validation():
    url = "https://aplicacoes.mds.gov.br/sagi/servicos/misocial/?fq=anomes_s:20*&q=*:*&rows=1000000&sort=anomes_s%20desc,%20codigo_ibge%20asc&wt=csv&fl=codigo_ibge,anomes_s,agricultores_fornec_paa_i,recur_pagos_agricul_paa_f&fq=agricultores_fornec_paa_i:*"
    output_path = 'data/raw/paa_execucao_geral.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Iniciando download da base histórica do PAA...")
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Download concluído: {output_path}")
    except Exception as e:
        print(f"Erro no download: {e}")
        return

    # Processamento
    print("Processando dados para validação (Ceará 2015)...")
    df = pd.read_csv(output_path)
    
    # Garantir tipos corretos
    df['codigo_ibge'] = df['codigo_ibge'].astype(str)
    df['anomes_s'] = df['anomes_s'].astype(str)
    
    # Filtrar Ceará (IBGE começa com 23) e Ano 2015
    df_ce_2015 = df[
        (df['codigo_ibge'].str.startswith('23')) & 
        (df['anomes_s'].str.startswith('2015'))
    ].copy()
    
    total_pago = df_ce_2015['recur_pagos_agricul_paa_f'].sum()
    total_agricultores = df_ce_2015['agricultores_fornec_paa_i'].sum()

    print("\n" + "="*40)
    print("RESULTADO DA VALIDAÇÃO - CEARÁ 2015")
    print("="*40)
    print(f"Total de Recursos Pagos: R$ {total_pago:,.2f}")
    print(f"Total de Agricultores:  {total_agricultores:,}")
    print("="*40)

    # Benchmark: R$ 12.7 milhões
    if 12000000 <= total_pago <= 13500000:
        print(">>> SUCESSO: O dado bate com o estudo de referência (12.7M)!")
    else:
        print(">>> ATENÇÃO: O valor difere do estudo. Verifique se o estudo refere-se a uma modalidade específica ou fonte CONAB.")

if __name__ == "__main__":
    run_validation()
