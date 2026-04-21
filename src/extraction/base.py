import requests
import json
import os
from pathlib import Path
from datetime import datetime
from src.core.config import BRONZE_DIR, DEFAULT_HEADERS
from src.core.logger import get_logger
from src.utils.helpers import get_file_hash, create_metadata

logger = get_logger(__name__)

class BaseExtractor:
    def __init__(self, provider_name: str):
        self.provider = provider_name
        self.output_dir = BRONZE_DIR / self.provider
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _save_raw(self, content, file_name: str, source_url: str, format: str = 'json'):
        """
        Salva o dado bruto e gera o arquivo de metadados correspondente.
        """
        file_path = self.output_dir / file_name
        
        logger.info(f"Salvando arquivo bruto em: {file_path}")
        
        if format == 'json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=4, ensure_ascii=False)
        else:
            with open(file_path, 'wb') as f:
                f.write(content)
                
        # Gera metadados
        metadata = create_metadata(file_path, source_url, self.provider)
        meta_path = file_path.with_suffix('.meta.json')
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Metadados salvos em: {meta_path}")
        return file_path

    def fetch(self, url: str, params: dict = None):
        """Faz a requisição HTTP com tratamento de erro básico."""
        try:
            response = requests.get(url, params=params, headers=DEFAULT_HEADERS, verify=False, timeout=30)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"Erro ao acessar {url}: {e}")
            raise
