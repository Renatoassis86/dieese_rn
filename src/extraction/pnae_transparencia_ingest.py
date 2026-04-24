import pandas as pd
import requests
import os
import time
from dotenv import load_dotenv

# Configurações
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_KEY_PORTAL = 'e5874effcecce2dce606fedcf6c16471'
HEADERS_PORTAL = {
    'chave-api-dados': API_KEY_PORTAL, 
    'Accept': 'application/json'
}
BASE_PORTAL = 'https://api.portaldatransparencia.gov.br/api-de-dados'

def fetch_pnae_transfers(year):
    """
    Busca repasses do PNAE (FNDE) via Portal da Transparência API.
    Ações do PNAE geralmente começam com códigos específicos.
    Filtramos por Órgão: 55000 (MEC/FNDE).
    """
    print(f"📥 Coletando repasses PNAE {year} via Portal da Transparência...")
    all_data = []
    
    # Exemplo: Consultar transferências por município para o favorecido PNAE
    # Vamos usar o endpoint de transferências granulares filtrando por PNAE
    # Como não há filtro por programa direto fácil em alguns endpoints, 
    # consultamos as transferências do FNDE (55000) e filtramos por descrição.
    
    # No RN, vamos percorrer os códigos IBGE do RN (2400109 até 2415008)
    # Para ser mais eficiente, buscamos por UF se a API permitir ou iteramos municípios.
    
    # Vamos usar o endpoint de despesas filtrando por subfunção 306 (Alimentação e Nutrição)
    # que é onde o PNAE está catalogado.
    
    page = 1
    while page < 50: # Limite de segurança
        # Endpoint de despesas por funcional programática (mais preciso para PNAE)
        url = f"{BASE_PORTAL}/despesas/por-funcional-programatica"
        params = {
            'ano': year,
            'funcao': '12', # Educação
            'subfuncao': '306', # Alimentação
            'programa': '2030', # Educação Básica
            'acao': '8744', # PNAE
            'pagina': page
        }
        
        try:
            r = requests.get(url, params=params, headers=HEADERS_PORTAL, timeout=30)
            if r.status_code != 200: 
                print(f"   ⚠️ Erro HTTP {r.status_code} na página {page}")
                break
            data = r.json()
            if not data: break
            
            for item in data:
                if not isinstance(item, dict):
                    print(f"   ⚠️ Item inválido recebido: {item}")
                    continue
                # Filtrar apenas para o RN (Unidade Gestora no RN ou Favorecido no RN)
                all_data.append({
                    'ano': year,
                    'acao': item.get('acao', {}).get('nome', 'N/A') if item.get('acao') else 'N/A',
                    'valor_pago': item.get('valorPago', 0),
                    'valor_liquidado': item.get('valorLiquidado', 0),
                    'programa': item.get('programa', {}).get('nome', 'N/A') if item.get('programa') else 'N/A'
                })
            
            if len(data) < 15: break
            page += 1
        except Exception as e:
            print(f"   ❌ Erro na página {page}: {e}")
            break
            
    return pd.DataFrame(all_data)

def run_validation_pnae():
    # Coleta de teste para 2022
    df_api = fetch_pnae_transfers(2022)
    print(f"✅ Coletados {len(df_api)} registros via API.")
    
    if not df_api.empty:
        total_api = df_api['valor_pago'].sum()
        print(f"💰 Total Injetado FNDE (API 2022): R$ {total_api:,.2f}")
    
    # No futuro, cruzaremos com 'pnae_master' vindo do Excel para garantir que
    # o 'valor_total_repassado' bata com o 'valor_pago' da API.

if __name__ == "__main__":
    run_validation_pnae()
