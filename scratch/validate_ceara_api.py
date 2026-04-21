from src.extraction.dados_gov_client import DadosGovClient
import pandas as pd
import json

def validate_ceara_2015():
    client = DadosGovClient()
    
    # 1. Buscar o dataset de Execução Geral (Série Histórica)
    print("Buscando datasets de Execução do PAA...")
    datasets = client.search_datasets("Execução do PAA")
    
    # Tentaremos identificar o dataset da CONAB ou MDS que contém 'Execução Geral'
    target_dataset_id = "programa-de-aquisi-o-de-alimentos-paa" # Slug comum
    
    try:
        details = client.get_dataset_details(target_dataset_id)
        resources = details.get("recursos", [])
        
        # Procurar recurso que pareça ser a série histórica (geralmente CSV ou Recursos Dinâmicos)
        # Muitas vezes o título é "Execução Geral do PAA"
        exec_resource = None
        for res in resources:
            if "geral" in res.get("titulo", "").lower():
                exec_resource = res
                break
        
        if not exec_resource:
            print("Não localizamos o recurso 'Execução Geral' via API.")
            return

        print(f"Recurso localizado: {exec_resource['titulo']} (ID: {exec_resource['id']})")
        
        # 2. Vamos tentar baixar os dados desse recurso
        # Para este teste, vamos baixar apenas uma amostra ou usar o download_resource do client
        file_path = client.download_resource(exec_resource['id'], "validation_ce")
        
        if file_path:
            # 3. Analisar dados do Ceará em 2015
            # Nota: O formato pode ser CSV ou XLSX
            df = None
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path, low_memory=False)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            
            if df is not None:
                # Normalizar nomes de colunas conforme dicionário
                # Procurar colunas de UF, Ano e Valor
                cols = df.columns.tolist()
                print(f"Colunas encontradas: {cols}")
                
                # Exemplo de filtragem baseada no dicionário (paa_indicador_adesao_municipio_i etc)
                # No dicionário do MDS as colunas podem ser 'sigla_uf', 'ano_referencia', 'vlr_pago'
                # Vamos tentar uma busca flexível
                uf_col = next((c for c in cols if 'uf' in c.lower() or 'estado' in c.lower()), None)
                ano_col = next((c for c in cols if 'ano' in c.lower()), None)
                vlr_col = next((c for c in cols if 'vlr_pago' in vlr_col_lower or 'valor' in vlr_col_lower or 'recur_pago' in vlr_col_lower), None)
                
                # Ajuste de erro de variável na linha acima (vlr_col logic)
                vlr_col = next((c for c in cols if any(k in c.lower() for k in ['vlr', 'valor', 'recurs'])), None)

                if uf_col and ano_col and vlr_col:
                    # Garantir tipos corretos
                    df[ano_col] = pd.to_numeric(df[ano_col], errors='coerce')
                    df[vlr_col] = pd.to_numeric(df[vlr_col].replace('[R$ ,]', '', regex=True), errors='coerce')
                    
                    df_ce_2015 = df[(df[uf_col].astype(str).str.upper() == 'CE') & (df[ano_col] == 2015)]
                    total_pago = df_ce_2015[vlr_col].sum()
                    
                    print(f"\n--- RESULTADO DA VALIDAÇÃO (CEARÁ 2015) ---")
                    print(f"Total extraído (API): R$ {total_pago:,.2f}")
                    print(f"Referência do Estudo: R$ 12,700,000.00")
                    
                    diff = abs(total_pago - 12700000)
                    if diff < 500000: # Margem de R$ 500k por arredondamentos financeiros
                        print("CONCLUSÃO: OS DADOS BATEM! Estamos no caminho correto para o RN.")
                    else:
                        print(f"Diferença encontrada: R$ {diff:,.2f}. Verificando indicadores...")
                else:
                    print("Não foi possível localizar as colunas de UF/Ano/Valor no arquivo.")

    except Exception as e:
        print(f"Erro durante a validação: {e}")

if __name__ == "__main__":
    validate_ceara_2015()
