# src/schema.py
import pandas as pd
from .schema_period import coerce_periodo, quarter_order_key

def standardize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Renomeia colunas usuais para um vocabulário mínimo.
    - Converte 'trimestre' -> 'periodo' no formato 'YYYYTQ'.
    - Converte colunas de taxa para numérico (0–100).
    """
    df = df.copy()
    # normalizações
    ren = {
        "trimestre": "periodo",
        "tx_informalidade": "tx_informalidade",
        "local": "local",
    }
    for k, v in ren.items():
        if k in df.columns:
            df.rename(columns={k: v}, inplace=True)

    if "periodo" in df.columns:
        df["periodo"] = coerce_periodo(df["periodo"])
        df["_ord"] = quarter_order_key(df["periodo"])
    # taxas (se existirem)
    for col in ("tx_informalidade", "tx_subocup", "tx_composta"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df
