# src/schema_period.py
from __future__ import annotations
import re
import pandas as pd

_TRIM_RX = re.compile(r"^\s*(\d{1})º?\s*tri\s*/\s*(\d{4})\s*$", flags=re.IGNORECASE)

def coerce_periodo(s: pd.Series) -> pd.Series:
    """
    Converte strings tipo '4º tri/2019' em rótulo padronizado '2019T4'
    e cria uma ordem temporal consistente.
    """
    def _coerce_one(x: str) -> str:
        if pd.isna(x):
            return x
        x = str(x)
        m = _TRIM_RX.match(x)
        if not m:
            return x  # deixa como está, se não casar
        tri = int(m.group(1))
        ano = int(m.group(2))
        return f"{ano}T{tri}"
    return s.map(_coerce_one)

def quarter_order_key(s: pd.Series) -> pd.Series:
    """
    Gera chave ordenável YYYY*4 + Q para sort exato por trimestre.
    Ex.: 2019T4 -> 2019*4 + 4
    """
    def _k(x: str):
        m = re.match(r"^(\d{4})T([1-4])$", str(x))
        if not m:
            return float("inf")
        return int(m.group(1)) * 4 + int(m.group(2))
    return s.map(_k)
