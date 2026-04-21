import json
from pathlib import Path
from typing import List, Dict, Optional

from src.extraction.base import BaseExtractor
from src.core.logger import get_logger

logger = get_logger("dados_gov_client")

class DadosGovClient(BaseExtractor):
    def __init__(self):
        super().__init__(provider_name="dados_gov")
        self.base_api_url = "https://dados.gov.br/dados/api/publico"

    def search_datasets(self, query: str) -> List[Dict]:
        """
        Busca conjuntos de dados por palavra-chave.
        Endpoint: /conjuntos-dados
        """
        url = f"{self.base_api_url}/conjuntos-dados"
        params = {"q": query}
        
        logger.info(f"Buscando datasets com o termo: '{query}'")
        response = self.fetch(url, params=params)
        data = response.json()
        
        # O Portal retorna uma estrutura 'content' com a lista
        results = data.get("content", [])
        logger.info(f"Encontrados {len(results)} conjuntos de dados.")
        return results

    def get_dataset_details(self, dataset_id: str) -> Dict:
        """
        Obtém detalhes de um conjunto de dados, incluindo seus recursos (arquivos).
        """
        url = f"{self.base_api_url}/conjuntos-dados/{dataset_id}"
        logger.info(f"Obtendo detalhes do dataset: {dataset_id}")
        
        response = self.fetch(url)
        return response.json()

    def download_resource(self, resource_id: str, dataset_title: str) -> Optional[Path]:
        """
        Baixa um recurso específico via Resource ID.
        """
        # A URL de download geralmente segue o padrão /recurso/baixar
        url_download = f"https://dados.gov.br/recurso/baixar/{resource_id}"
        
        try:
            logger.info(f"Iniciando download do recurso {resource_id}...")
            response = self.fetch(url_download)
            
            # Tenta extrair o nome do arquivo do header ou usa um padrão
            content_disposition = response.headers.get('content-disposition', '')
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
            else:
                filename = f"recurso_{resource_id}.bin"

            # Salva na camada Bronze usando a BaseExtractor
            file_path = self._save_raw(response.content, filename, url_download, format='binary')
            return file_path

        except Exception as e:
            logger.error(f"Erro ao baixar recurso {resource_id}: {e}")
            return None

    def ingest_paa_latest(self) -> Optional[Path]:
        """
        Fluxo completo: busca PAA, encontra o dataset da Conab e baixa o recurso de Entregas.
        """
        datasets = self.search_datasets("Programa de Aquisição de Alimentos")
        
        # Filtrar pelo dataset da CONAB (usualmente 'programa-de-aquisi-o-de-alimentos-paa')
        # ou buscar o que contém 'Conab' na organização
        paa_dataset = None
        for ds in datasets:
            if "conab" in ds.get("nome", "").lower() or "conab" in ds.get("organizacao", {}).get("nome", "").lower():
                paa_dataset = ds
                break
        
        if not paa_dataset:
            logger.warning("Dataset PAA da Conab não encontrado na busca inicial.")
            return None

        # Obter detalhes para listar os recursos
        details = self.get_dataset_details(paa_dataset['id'])
        resources = details.get("recursos", [])
        
        # Procurar o recurso de 'Entregas' (preferencialmente CSV ou XLSX)
        target_resource = None
        for res in resources:
            title = res.get("titulo", "").lower()
            if "entrega" in title and res.get("formato", "").lower() in ["csv", "xlsx"]:
                target_resource = res
                break
        
        if target_resource:
            logger.info(f"Recurso de Entregas localizado: {target_resource['titulo']}")
            return self.download_resource(target_resource['id'], paa_dataset['titulo'])
        
        logger.warning("Recurso de 'Entregas' não localizado no dataset do PAA.")
        return None

if __name__ == "__main__":
    client = DadosGovClient()
    # Teste de busca
    client.ingest_paa_latest()
