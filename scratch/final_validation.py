import requests
import json

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJfU1ozX0hqOXpTSnUzb19vX1ZmX0RRemNhZWxzb254NklhQS03QUs4aUhMeWFVaW1yX2EzUmw5cTBRSm5LbmVtYTh1c0FNTnZ4YXI3VlhLOSIsImlhdCI6MTc3Njc4OTYzMn0.NVUqTbkdV__bAW7OeN7xYHWMAzCLP82O7XMnPgvnQYA"
BASE_URL = "https://dados.gov.br/api/3/action"

def get_paa_data():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": "Mozilla/5.0"
    }
    
    print("1. Buscando metadados do PAA...")
    try:
        response = requests.get(
            f"{BASE_URL}/package_show", 
            params={"id": "programa-de-aquisi-o-de-alimentos-paa"},
            headers=headers,
            verify=False
        )
        response.raise_for_status()
        pkg = response.json()
        
        resources = pkg['result']['resources']
        # Buscar o ID do recurso 'Execução Geral'
        exec_id = None
        for res in resources:
            if "geral" in res['name'].lower():
                exec_id = res['id']
                print(f"   Recurso encontrado: {res['name']} (ID: {exec_id})")
                break
        
        if not exec_id:
            print("   Recurso 'Execução Geral' não encontrado.")
            return

        print(f"2. Consultando dados do Ceará (2015) no recurso {exec_id}...")
        # SQL API do CKAN
        sql = f"SELECT SUM(cast(recur_pagos_agricul_paa_f as numeric)) as total FROM \"{exec_id}\" WHERE sigla_uf = 'CE' AND ano_referencia = 2015"
        
        # Como o SQL pode ser complexo dependendo da versão do CKAN, vamos tentar o datastore_search
        search_params = {
            "resource_id": exec_id,
            "filters": '{"sigla_uf": "CE", "ano_referencia": 2015}',
            "limit": 1000
        }
        
        res_search = requests.get(f"{BASE_URL}/datastore_search", params=search_params, headers=headers, verify=False)
        res_search.raise_for_status()
        results = res_search.json()['result']['records']
        
        if not results:
            print("   Nenhum registro encontrado para CE em 2015.")
            return

        total_pago = 0
        for rec in results:
            # Limpeza de valor (string para float)
            v = rec.get('recur_pagos_agricul_paa_f')
            if v:
                try:
                    total_pago += float(str(v).replace(',', '.'))
                except:
                    pass
        
        print(f"\n--- RESULTADO DA BATIDA DE DADOS ---")
        print(f"Valor Extraído da API: R$ {total_pago:,.2f}")
        print(f"Valor no Estudo DIEESE: R$ 12,700,000.00")
        
        if 12000000 < total_pago < 13500000:
            print("STATUS: DADOS COINCIDENTES! A extração está correta.")
        else:
            print("STATUS: DIVERGÊNCIA ENCONTRADA. Reavaliando indicadores...")

    except Exception as e:
        print(f"Erro na comunicação: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    get_paa_data()
