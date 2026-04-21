import os
import shutil
from pathlib import Path
from src.extraction.base import BaseExtractor
from src.core.config import BASE_DIR, UF_FOCO
from src.core.logger import get_logger

logger = get_logger(__name__)

class CONABExtractor(BaseExtractor):
    def __init__(self):
        super().__init__(provider_name="conab")
        
    def extract_from_local_docs(self):
        """
        Como arquivos da CONAB são frequentemente PDFs ou Planilhas manuais, 
        esta função busca arquivos na pasta /docs que correspondam ao padrão PAA 
        e os copia para a camada Bronze com metadados.
        """
        logger.info("Buscando arquivos CONAB PAA na pasta docs...")
        docs_dir = BASE_DIR / "docs"
        
        # Padrões comuns
        patterns = ["*PAA*", "*Execucao*", "*Compendio*"]
        
        found_files = []
        for pattern in patterns:
            found_files.extend(list(docs_dir.glob(pattern)))
            
        for source_file in set(found_files):
            if source_file.suffix.lower() in ['.pdf', '.xlsx', '.xls', '.csv']:
                logger.info(f"Ingerindo arquivo CONAB: {source_file.name}")
                
                # Para arquivos locais, a URL de origem é o caminho original
                file_name = f"local_{source_file.name}"
                
                with open(source_file, 'rb') as f:
                    content = f.read()
                    
                self._save_raw(content, file_name, f"file://{source_file}", format='binary')
                
    def extract_paa_deliveries(self):
        """
        Placeholder para extração via API do Portal de Informações da CONAB.
        """
        # URL da dashboard: https://portaldeinformacoes.conab.gov.br/paa-propostas.html
        # Implementação futura para capturar o JSON do backend do dashboard
        logger.warning("Coleta via API CONAB (Dashboard) ainda não mapeada. Use a ingestão local por enquanto.")

if __name__ == "__main__":
    extractor = CONABExtractor()
    extractor.extract_from_local_docs()
