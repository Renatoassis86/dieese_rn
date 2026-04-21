"""
Major Update: Comprehensive Territorial Mapping for RN.
Maps remaining municipalities to ensure charts are coherent and don't show 'Outros'.
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Expanded Official Mapping for RN
COMPREHENSIVE_TERRITORIES = {
    "Alto Oeste": ["Pau dos Ferros", "Apodi", "Umarizal", "Alexandria", "São Miguel", "Portalegre", "Martins", "Almino Afonso", "Antônio Martins", "Doutor Severiano", "Encanto", "Francisco Dantas", "Frutuoso Gomes", "Itaú", "João Dias", "José da Penha", "Lucrécia", "Luís Gomes", "Major Sales", "Marcelino Vieira", "Olho-d'Água do Borges", "Paraná", "Patu", "Pilões", "Rafael Fernandes", "Riacho da Cruz", "Riacho de Santana", "Rodolfo Fernandes", "Serrinha dos Pintos", "Severiano Melo", "Taboleiro Grande", "Tenente Ananias", "Viçosa"],
    "Seridó": ["Caicó", "Currais Novos", "Parelhas", "Jardim do Seridó", "Acari", "São João do Sabugi", "Bodó", "Carnaúba dos Dantas", "Cruzeta", "Equador", "Florânia", "Ipueira", "Jardim de Piranhas", "Jucurutu", "Lagoa Nova", "Ouro Branco", "Santana do Seridó", "São Fernando", "São José do Seridó", "São Vicente", "Serra Negra do Norte", "Tenente Laurentino Cruz", "Timbaúba dos Batistas"],
    "Assú-Mossoró": ["Mossoró", "Assú", "Tibau", "Baraúna", "Serra do Mel", "Areia Branca", "Carnaubais", "Grossos", "Ipanguaçu", "Itajá", "Porto do Mangue", "Pendências", "Upanema"],
    "Sertão do Apodi": ["Apodi", "Felipe Guerra", "Itaú", "Severiano Melo", "Rodolfo Fernandes", "Gov. Dix-Sept Rosado"],
    "Mato Grande": ["João Câmara", "Ceará-Mirim", "Touros", "Taipu", "Poço Branco", "Bento Fernandes", "Jandaíra", "Jardim de Angicos", "Maxaranguape", "Parazinho", "Pedra Grande", "Pureza", "Rio do Fogo", "São Bento do Norte", "São Miguel do Gostoso"],
    "Potengi": ["São Paulo do Potengi", "Santa Maria", "Riachuelo", "São Tomé", "Barcelona", "Bento Fernandes", "Ielmo Marinho", "Lagoa de Velhos", "Ruy Barbosa", "São Pedro", "Senador Elói de Souza"],
    "Trairi": ["Santa Cruz", "Tangará", "Sítio Novo", "Lajes Pintadas", "Coronel Ezequiel", "Boa Saúde", "Campo Redondo", "Jaçanã", "Japi", "Lajes Pintadas", "Passa e Fica", "São Bento do Trairi", "Serra de São Bento"],
    "Agreste Litoral Sul": ["Goianinha", "Canguaretama", "Pipa", "Tibau do Sul", "Santo Antônio", "Nova Cruz", "Arês", "Baía Formosa", "Brejinho", "Espírito Santo", "Jundiá", "Lagoa d'Anta", "Lagoa de Pedras", "Lagoa Salgada", "Montanhas", "Monte Alegre", "Passagem", "Serrinha", "Várzea"],
    "Terras Potiguares": ["Natal", "Parnamirim", "São Gonçalo do Amarante", "Macaíba", "Extremoz", "Ceará-Mirim", "Nísia Floresta", "São José de Mipibu", "Vera Cruz"],
    "Sertão Central Cabugi e Litoral Norte": ["Lajes", "Angicos", "Pedro Avelino", "Galinhos", "Macau", "Guamaré", "Afonso Bezerra", "Caiçara do Norte", "Caiçara do Rio do Vento", "Fernando Pedroza", "Jardim de Angicos", "Pedra Preta", "Santana do Matos", "São Rafael"]
}

def get_municipio_ibge(nome):
    try:
        with open('data/raw/municipios_rn.json', 'r', encoding='utf-16') as f:
            data = json.load(f)['value']
            for m in data:
                if m['nome'].lower() == nome.lower():
                    return str(m['id'])
    except: pass
    return None

def populate():
    print("🚀 Realizando mapeamento territorial abrangente do RN...")
    rows = []
    seen = set()
    for terr, mun_list in COMPREHENSIVE_TERRITORIES.items():
        for m_name in mun_list:
            m_id = get_municipio_ibge(m_name)
            if m_id and m_id not in seen:
                rows.append({"nome_territorio": terr, "nome_municipio": m_name, "cod_municipio_ibge": m_id})
                seen.add(m_id)
    
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    api_url = f"{SUPABASE_URL}/rest/v1/territorios_rn"
    
    # Clean and Refill
    requests.delete(api_url, headers=headers)
    res = requests.post(api_url, headers=headers, json=rows)
    print(f"✅ {len(rows)} municípios mapeados aos territórios!")

if __name__ == "__main__":
    populate()
