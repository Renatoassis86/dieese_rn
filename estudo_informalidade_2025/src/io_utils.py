# src/io_utils.py
from __future__ import annotations
from pathlib import Path
from typing import Optional, Sequence
import pandas as pd

from .config import PROJECT_DIR

DATA_DIR_CANDIDATES: Sequence[Path] = (
    PROJECT_DIR / "data",
    PROJECT_DIR,  # fallback
)

def _resolve_data_path(filename: str | Path) -> Path:
    p = Path(filename)
    if p.exists():
        return p
    for base in DATA_DIR_CANDIDATES:
        candidate = (base / p)
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Arquivo não encontrado em {DATA_DIR_CANDIDATES}: {filename}")

def read_csv_safely(filename: str | Path,
                    sep: Optional[str] = None,
                    decimal: Optional[str] = None,
                    encoding: Optional[str] = "utf-8",
                    dtype: Optional[dict] = None) -> pd.DataFrame:
    """
    Lê CSVs do projeto com defaults adequados a arquivos em português (sep=';' e decimal=',').
    - Detecta caminho automaticamente (data/ e raiz do projeto).
    - Não usa parâmetros incompatíveis com pandas (como 'errors' em read_csv).
    - Mantém dtype customizado quando necessário.
    """
    path = _resolve_data_path(filename)
    if sep is None:
        sep = ";"
    if decimal is None:
        decimal = ","

    try:
        df = pd.read_csv(path, sep=sep, decimal=decimal, encoding=encoding, dtype=dtype)
    except UnicodeDecodeError:
        # fallback simples
        df = pd.read_csv(path, sep=sep, decimal=decimal, encoding="latin-1", dtype=dtype)

    # limpeza básica de nomes de colunas
    df.columns = (
        df.columns
          .str.strip()
          .str.replace(r"\s+", " ", regex=True)
          .str.replace("\ufeff", "", regex=False)
    )
    return df
