import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Caminhos base
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

# Garantir que diretórios existam
for dir_path in [BRONZE_DIR, SILVER_DIR, GOLD_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Configurações do Banco de Dados
DB_PATH = DATA_DIR / "paa_observatorio.duckdb"
DATABASE_URL = os.getenv("DATABASE_URL", f"duckdb:///{DB_PATH}")

# Tokens e Autenticação
DADOS_GOV_BR_TOKEN = os.getenv("DADOS_GOV_BR_TOKEN")

# Configurações de Extração
UF_FOCO = "RN"
IBGE_RN_ID = "24"

# URLs de Referência
URL_PAA_DADOS_ABERTOS = "https://dados.gov.br/dados/conjuntos-dados/programa-de-aquisi-o-de-alimentos-paa"
URL_CONAB_PAA = "https://www.conab.gov.br/info-agro/paa"

# Headers padrão para requisições governamentais
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

if DADOS_GOV_BR_TOKEN:
    DEFAULT_HEADERS["Authorization"] = f"Bearer {DADOS_GOV_BR_TOKEN}"
