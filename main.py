import sys
from src.core.logger import get_logger
from src.storage.database import DatabaseManager

logger = get_logger("paa_orchestrator")

def run_pipeline():
    """
    Função principal para orquestrar o pipeline PAA RN.
    """
    logger.info("Iniciando Pipeline de Dados PAA - Observatório RN")
    
    try:
        # FASE 3: Extração (Bronze)
        # TODO: Chamar extrator
        logger.info("Fase Bronze: Extração pendente de implementação (Fase 3)")
        
        # FASE 4: Transformação (Silver)
        # TODO: Chamar transformador
        logger.info("Fase Silver: Transformação pendente de implementação (Fase 4)")
        
        # FASE 5: Modelagem Dimensional (Gold)
        # TODO: Gerar marts
        logger.info("Fase Gold: Marts pendentes de implementação (Fase 5)")
        
        logger.info("Pipeline finalizado com sucesso.")
        
    except Exception as e:
        logger.error(f"Erro crítico no pipeline: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
