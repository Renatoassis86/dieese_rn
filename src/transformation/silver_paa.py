import pandas as pd
import json
from pathlib import Path
from src.core.config import BRONZE_DIR, SILVER_DIR
from src.core.logger import get_logger
from src.storage.database import DatabaseManager

logger = get_logger(__name__)

class SilverTransformer:
    def __init__(self):
        self.db = DatabaseManager()
        self.silver_dir = SILVER_DIR
        self.silver_dir.mkdir(parents=True, exist_ok=True)
        
    def process_municipalities(self):
        """
        Transforma a lista bruta de municípios do IBGE em uma tabela dimensional limpa.
        """
        logger.info("Processando municípios (Bronze -> Silver)...")
        bronze_path = BRONZE_DIR / "ibge" / "municipios_rn.json"
        
        if not bronze_path.exists():
            logger.error("Arquivo de municípios não encontrado na Bronze.")
            return
            
        with open(bronze_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Normalização do JSON do IBGE
        df = pd.DataFrame([
            {
                "codigo_ibge": str(m["id"]),
                "municipio": m["nome"],
                "microrregiao": m["microrregiao"]["nome"],
                "mesorregiao": m["microrregiao"]["mesorregiao"]["nome"],
                "uf": "RN"
            } for m in data
        ])
        
        output_path = self.silver_dir / "dim_municipios.parquet"
        df.to_parquet(output_path, index=False)
        self.db.save_dataframe(df, "dim_municipios")
        logger.info(f"Tabela dim_municipios salva em Parquet e DuckDB.")
        return df

    def process_paa_execution(self, bronze_file_name: str):
        """
        Transforma os dados brutos de execução do PAA em uma tabela fato normalizada.
        """
        logger.info(f"Processando PAA Execution ({bronze_file_name})...")
        bronze_path = BRONZE_DIR / "mds" / bronze_file_name
        
        if not bronze_path.exists():
            logger.warning(f"Arquivo {bronze_file_name} não encontrado na Bronze.")
            return

        # Tenta ler como JSON (formato da nossa extração via API)
        try:
            with open(bronze_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                records = raw_data.get("result", {}).get("records", [])
                df = pd.DataFrame(records)
        except Exception as e:
            logger.error(f"Erro ao ler JSON: {e}. Tentando ler como CSV/Excel...")
            # Fallback para outros formatos se o usuário baixar manualmente
            if bronze_path.suffix == '.csv':
                df = pd.read_csv(bronze_path)
            else:
                return # Adicionar suporte a Excel se necessário

        # Mapeamento de colunas (conforme dicionario_paa.md)
        # Este mapeamento deve ser ajustado conforme as colunas reais retornadas
        column_mapping = {
            "ano_referencia": "ano",
            "mes_referencia": "mes",
            "sigla_uf": "uf",
            "nome_municipio": "municipio",
            "codigo_ibge": "codigo_ibge",
            "vl_pagamento": "valor_rs",
            "nu_agricultores": "qtd_agricultores"
        }
        
        # Filtra e renomeia
        df = df.rename(columns=column_mapping)
        
        # Garantir tipos
        if 'valor_rs' in df.columns:
            df['valor_rs'] = pd.to_numeric(df['valor_rs'], errors='coerce').fillna(0)
        if 'codigo_ibge' in df.columns:
            df['codigo_ibge'] = df['codigo_ibge'].astype(str)
            
        output_path = self.silver_dir / "fato_paa_execucao.parquet"
        df.to_parquet(output_path, index=False)
        self.db.save_dataframe(df, "fato_paa_execucao")
        logger.info(f"Tabela fato_paa_execucao salva em Parquet e DuckDB.")
        return df

if __name__ == "__main__":
    transformer = SilverTransformer()
    transformer.process_municipalities()
    # transformer.process_paa_execution("paa_execution_sample.json")
