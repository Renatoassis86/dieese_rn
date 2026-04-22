# scripts/_smoke_standardize.py
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.schema import standardize_dataframe

CSV_PATH = ROOT / "data" / "T1_informalidade_total.csv"

def main():
    df = pd.read_csv(CSV_PATH, sep=";", decimal=",", encoding="utf-8-sig")
    std = standardize_dataframe(df)

    print("== dtypes após padronização ==")
    print(std.dtypes)
    print("\n== amostra ==")
    cols = [c for c in ["periodo","grupo","taxa_informalidade","ocupados_k","informais_k"] if c in std.columns]
    print(std.head(10)[cols].to_string(index=False))

if __name__ == "__main__":
    main()
