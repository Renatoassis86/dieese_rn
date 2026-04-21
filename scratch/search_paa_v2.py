import requests
import json
import os

def search_paa_datasets():
    # Trying different combinations to get around 401
    base_url = "https://dados.gov.br/api/3/action/package_search"
    query = "PAA"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    params = {
        "q": query,
        "rows": 50
    }
    
    try:
        print(f"Searching for '{query}' on dados.gov.br with headers...")
        response = requests.get(base_url, params=params, headers=headers, verify=False, timeout=30)
        
        if response.status_code == 401:
            print("Received 401. Trying without HTTPS (HTTP)...")
            response = requests.get(base_url.replace("https", "http"), params=params, headers=headers, timeout=30)
            
        response.raise_for_status()
        data = response.json()
        
        results = data.get("result", {}).get("results", [])
        print(f"Success! Found {len(results)} packages.")
        
        # ... rest of the extraction logic ...
        output = []
        for pkg in results:
            pkg_info = {
                "title": pkg.get("title"),
                "name": pkg.get("name"),
                "id": pkg.get("id"),
                "resources": []
            }
            for res in pkg.get("resources", []):
                pkg_info["resources"].append({
                    "name": res.get("name"),
                    "id": res.get("id"),
                    "url": res.get("url")
                })
            output.append(pkg_info)
            
        scratch_dir = r"d:\repositorio_geral\app_dieese\scratch"
        os.makedirs(scratch_dir, exist_ok=True)
        with open(os.path.join(scratch_dir, "paa_final_results.json"), "w", encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    search_paa_datasets()
