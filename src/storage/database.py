import duckdb
from sqlalchemy import create_engine
from src.core.config import DB_PATH, DATABASE_URL
from src.core.logger import get_logger

logger = get_logger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.db_path = DB_PATH
        
    def execute_query(self, query: str):
        """Executa uma query direta via DuckDB."""
        with duckdb.connect(str(self.db_path)) as conn:
            return conn.execute(query).fetchdf()

    def save_dataframe(self, df, table_name: str, schema: str = 'main'):
        """Salva um DataFrame no banco de dados DuckDB."""
        logger.info(f"Salvando dados na tabela {schema}.{table_name}...")
        with duckdb.connect(str(self.db_path)) as conn:
            conn.execute(f"CREATE TABLE IF NOT EXISTS {schema}.{table_name} AS SELECT * FROM df")
            # Para inserções incrementais ou updates, a lógica seria expandida aqui
            
    def query_to_parquet(self, query: str, output_path: str):
        """Exporta o resultado de uma query diretamente para Parquet (performance Gold)."""
        with duckdb.connect(str(self.db_path)) as conn:
            conn.execute(f"COPY ({query}) TO '{output_path}' (FORMAT PARQUET)")
            logger.info(f"Dados exportados para {output_path}")
