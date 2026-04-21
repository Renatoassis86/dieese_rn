from src.extraction.base import BaseExtractor
from src.core.config import IBGE_RN_ID, UF_FOCO
from src.core.logger import get_logger

logger = get_logger(__name__)

class IBGEExtractor(BaseExtractor):
    def __init__(self):
        super().__init__(provider_name="ibge")
        
    def extract_municipalities(self):
        """
        Coleta a lista de municípios do RN via API do IBGE.
        """
        logger.info(f"Iniciando extração de municípios do {UF_FOCO}...")
        url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{IBGE_RN_ID}/municipios"
        
        response = self.fetch(url)
        data = response.json()
        
        file_name = f"municipios_{UF_FOCO.lower()}.json"
        return self._save_raw(data, file_name, url)

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    extractor = IBGEExtractor()
    extractor.extract_municipalities()
