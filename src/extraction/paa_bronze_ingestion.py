import requests
from pathlib import Path
import datetime
from typing import Optional

from src.core.config import BRONZE_DIR, DEFAULT_HEADERS, URL_CONAB_PAA
from src.core.logger import get_logger
from src.utils.helpers import create_metadata

logger = get_logger("paa_bronze")

class PAABronzeIngestor:
    def __init__(self):
        self.output_dir = BRONZE_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_file(self, url: str, resource_name: str, extension: str = "xlsx") -> Optional[Path]:
        """
        Faz o download de um arquivo da fonte oficial e salva na camada Bronze.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_conab_{resource_name}.{extension}"
        file_path = self.output_dir / filename

        logger.info(f"Iniciando download de {resource_name} via {url}...")

        try:
            response = requests.get(url, headers=DEFAULT_HEADERS, verify=False, timeout=60)
            response.raise_for_status()

            # Salva o conteúdo bruto
            with open(file_path, "wb") as f:
                f.write(response.content)

            # Gera metadados de rastreabilidade
            metadata = create_metadata(file_path, url, "CONAB")
            metadata_path = file_path.with_suffix(".json")
            
            import json
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4, ensure_ascii=False)

            logger.info(f"Sucesso! Arquivo salvo em {file_path}")
            logger.info(f"Hash do arquivo: {metadata['file_hash']}")
            
            return file_path

        except Exception as e:
            logger.error(f"Erro ao baixar {resource_name}: {e}")
            return None

    def ingest_latest_entregas(self):
        """
        Tenta ingerir a base mais recente de 'Entregas' do PAA.
        Nota: A URL abaixo é o endpoint comum para a base de dados abertos da Conab.
        """
        # Esta URL pode precisar de ajuste manual caso a Conab mude o ID do recurso
        # Exemplo baseado no dataset 'Programa de Aquisição de Alimentos - Entregas'
        url_entregas = "https://dados.gov.br/dataset/c290a618-9366-4c4f-9e73-b3c675306873/resource/bbf32d84-18c3-4f9e-bbb8-9e665d9e5db4/download/paa-entregas.csv"
        
        return self.download_file(url_entregas, "paa_entregas_geral", extension="csv")

    def ingest_compendio_historico(self, ano: int):
        """
        Ingere o compêndio histórico de um ano específico (Backfill).
        """
        # Exemplo de URL de compêndio
        url_historico = f"https://www.gov.br/conab/pt-br/atuacao/paa/execucao-do-paa/compendio-execucao-do-paa/acoes-conab-{ano}"
        logger.warning(f"Extração de compêndio {ano} requer parser HTML (BS4) na Fase 4. Salvando URL para referência.")
        # No momento, salvamos apenas a base principal. O backfill será tratado na Silver via leitura direta dos PDFs/XLSX manuais
        pass

if __name__ == "__main__":
    ingestor = PAABronzeIngestor()
    ingestor.ingest_latest_entregas()
