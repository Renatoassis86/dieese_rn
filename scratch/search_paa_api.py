import requests
import json
import os

def search_paa_datasets():
    base_url = "https://dados.gov.br/api/3/action/package_search"
    query = "Programa de Aquisição de Alimentos"
    
    params = {
        "q": query,
        "rows": 50
    }
    
    try:
        print(f"Searching for '{query}' on dados.gov.br...")
        # Note: Using verify=False because some corporate environments/proxies have issues with gov.br certificates
        response = requests.get(base_url, params=params, verify=False, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("result", {}).get("results", [])
        
        output = []
        for pkg in results:
            pkg_info = {
                "title": pkg.get("title"),
                "name": pkg.get("name"),
                "organization": pkg.get("organization", {}).get("title"),
                "resources": []
            }
            for res in pkg.get("resources", []):
                pkg_info["resources"].append({
                    "name": res.get("name"),
                    "format": res.get("format"),
                    "id": res.get("id"),
                    "url": res.get("url")
                })
            output.append(pkg_info)
            
        scratch_dir = r"d:\repositorio_geral\app_dieese\scratch"
        os.makedirs(scratch_dir, exist_ok=True)
        output_file = os.path.join(scratch_dir, "paa_api_results.json")
        
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
            
        print(f"\nFound {len(results)} packages. Details saved to {output_file}\n")
        for pkg in output:
            if "paa" in pkg['title'].lower() or "aquisição de alimentos" in pkg['title'].lower():
                print(f"Package: {pkg['title']} ({pkg['organization']})")
                for res in pkg['resources']:
                    if res['format'].upper() in ['CSV', 'JSON', 'XLS', 'XLSX']:
                        print(f"  * {res['name']} ({res['format']}): {res['id']}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    search_paa_datasets()
