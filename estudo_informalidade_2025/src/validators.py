# src/validators.py
from __future__ import annotations
import pandas as pd

def require_columns(df: pd.DataFrame, cols: list[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas faltantes: {missing}")

def assert_percentage_bounds(s: pd.Series, name: str) -> None:
    s_clean = pd.to_numeric(s, errors="coerce")
    if ((s_clean < 0) | (s_clean > 100)).any():
        bad = s_clean[(s_clean < 0) | (s_clean > 100)]
        raise ValueError(f"{name} fora de 0–100 em {len(bad)} linhas. Exemplos: {bad.head(3).to_list()}")

def assert_min_rows(df: pd.DataFrame, nmin: int, context: str) -> None:
    if len(df) < nmin:
        raise ValueError(f"Poucas linhas ({len(df)}) para {context}. Esperado pelo menos {nmin}.")
