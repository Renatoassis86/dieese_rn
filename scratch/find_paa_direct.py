import requests
import json

def try_datasets():
    datasets = [
        "execucao-do-programa-de-aquisicao-de-alimentos-paa",
        "paa-execucao-geral",
        "programa-de-aquisicao-de-alimentos-paa",
        "paa-pagamentos"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for ds in datasets:
        url = f"https://dados.gov.br/api/3/action/package_show?id={ds}"
        print(f"Trying {url}...")
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=15)
            if response.status_code == 200:
                print(f"SUCCESS for {ds}!")
                data = response.json()
                resources = data.get("result", {}).get("resources", [])
                for res in resources:
                    print(f"  - {res.get('name')}: {res.get('id')} ({res.get('format')})")
            else:
                print(f"Failed with status: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try_datasets()
