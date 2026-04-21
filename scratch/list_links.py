import requests
from bs4 import BeautifulSoup # I'll try to import beautifulsoup if available
import re

def list_links(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        
        # Simple regex if BS4 is not available
        links = re.findall(r'href=[\'"]?([^\'" >]+)', response.text)
        
        print(f"Links found in {url}:")
        for link in set(links):
            if any(ext in link.lower() for ext in ['.pdf', '.csv', '.xlsx', '.xls']):
                if link.startswith('/'):
                    link = "https://www.gov.br" + link
                print(f"- {link}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    list_links("https://www.gov.br/conab/pt-br/atuacao/paa/execucao-do-paa")
