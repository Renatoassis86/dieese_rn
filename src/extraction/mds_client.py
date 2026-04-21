from src.extraction.base import BaseExtractor
from src.core.config import UF_FOCO
from src.core.logger import get_logger

logger = get_logger(__name__)

class MDSExtractor(BaseExtractor):
    def __init__(self):
        super().__init__(provider_name="mds")
        
    def extract_paa_api(self, resource_id: str):
        """
        Coleta dados do PAA via API do dados.gov.br (CKAN).
        """
        logger.info(f"Acessando API dados.gov.br para resource: {resource_id}...")
        url = "https://dados.gov.br/api/3/action/datastore_search"
        params = {
            "resource_id": resource_id,
            "q": UF_FOCO,
            "limit": 10000
        }
        
        try:
            response = self.fetch(url, params=params)
            data = response.json()
            
            file_name = f"paa_execution_{resource_id[:8]}.json"
            return self._save_raw(data, file_name, f"{url}?resource_id={resource_id}")
        except Exception as e:
            logger.error(f"Falha na extração da API MDS: {e}")
            logger.info("Sugestão: Realize o download manual do CSV no portal dados.gov.br e coloque em data/bronze/mds/manual_paa.csv")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    extractor = MDSExtractor()
    # Resource ID de exemplo (deve ser atualizado com o ID real do portal)
    extractor.extract_paa_api("paa-execucao-geral-id")
