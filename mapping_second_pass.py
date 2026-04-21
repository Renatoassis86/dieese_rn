"""
Second pass: Catching missing municipalities with name normalization.
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def normalize(name):
    import unicodedata
    s = "".join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    return s.lower().replace("-", " ").strip()

missing = ["Olho-d'Água do Borges", "Boa Saúde", "São Bento do Trairi", "Arês", "Lagoa d'Anta"]

TERRITORIO_MAP = {
    "Alto Oeste": ["Olho-d'Água do Borges"],
    "Trairi": ["Boa Saúde", "Passa e Fica", "São Bento do Trairi"],
    "Agreste Litoral Sul": ["Arês", "Lagoa d'Anta", "Lagoa de Pedras", "Lagoa Salgada"]
}

def get_municipio_6digit_ibge(nome):
    norm_nome = normalize(nome)
    try:
        with open('data/raw/municipios_rn.json', 'r', encoding='utf-16') as f:
            data = json.load(f)['value']
            for m in data:
                if normalize(m['nome']) == norm_nome:
                    return str(m['id'])[:6]
    except: pass
    return None

def populate_second_pass():
    print("🚀 Realizando segunda carga de mapeamento (normalização)...")
    rows = []
    
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    
    # Check what already exists to avoid duplicates
    existing = requests.get(f"{SUPABASE_URL}/rest/v1/territorios_rn?select=cod_municipio_ibge", headers=headers).json()
    seen = {e['cod_municipio_ibge'] for e in existing}

    for terr, mun_list in TERRITORIO_MAP.items():
        for m_name in mun_list:
            m_id = get_municipio_6digit_ibge(m_name)
            if m_id and m_id not in seen:
                rows.append({"nome_territorio": terr, "nome_municipio": m_name.upper(), "cod_municipio_ibge": m_id})
                seen.add(m_id)
    
    if rows:
        requests.post(f"{SUPABASE_URL}/rest/v1/territorios_rn", headers=headers, json=rows)
        print(f"✅ Mais {len(rows)} municípios adicionados com sucesso.")
    else:
        print("Nenhum município novo encontrado no second pass.")

if __name__ == "__main__":
    populate_second_pass()
