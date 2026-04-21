import pandas as pd
import requests
import os

def download_and_check_conab():
    files = {
        "2015": "https://www.gov.br/conab/pt-br/atuacao/paa/execucao-do-paa/compendio-execucao-do-paa/arquivos/paa-2015-detalhado.csv",
        "2021": "https://www.gov.br/conab/pt-br/atuacao/paa/execucao-do-paa/compendio-execucao-do-paa/arquivos/paa-2021-detalhado.csv"
    }
    
    for year, url in files.items():
        output = f'data/raw/paa_conab_{year}.csv'
        print(f"Baixando CONAB {year}...")
        try:
            r = requests.get(url, verify=False, timeout=30)
            if r.status_code == 200:
                with open(output, 'wb') as f:
                    f.write(r.content)
                print(f"  -> Concluído: {output}")
                
                # Checagem rápida
                try:
                    df = pd.read_csv(output, sep=None, engine='python', encoding='latin-1')
                    # Tentar achar a coluna de valor
                    val_col = [c for c in df.columns if 'valor' in c.lower() or 'pago' in c.lower()]
                    uf_col = [c for c in df.columns if 'uf' in c.lower() or 'estado' in c.lower()]
                    
                    if val_col and uf_col:
                        df_ce = df[df[uf_col[0]].astype(str).str.upper() == 'CE']
                        # Limpar valor se for string (remover R$, trocar vírgula por ponto)
                        soma = df_ce[val_col[0]].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float).sum()
                        print(f"  -> SOMA CEARÁ {year} (CONAB): R$ {soma:,.2f}")
                except Exception as e:
                    print(f"  -> Erro ao ler CSV: {e}")
            else:
                print(f"  -> Erro {r.status_code} ao baixar {year}. Link pode estar quebrado.")
        except Exception as e:
            print(f"  -> Falha: {e}")

if __name__ == "__main__":
    download_and_check_conab()
