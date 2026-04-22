# -*- coding: utf-8 -*-
# 14_previdencia_contribuicao.py
# Taxa de contribuição previdenciária dos ocupados — Formais x Informais
# Um gráfico por localidade (Brasil, Nordeste, Rio Grande do Norte)
# Barras agrupadas por ano (2019..2025): duas colunas (Formais, Informais)
# Métrica: pct_contrib (% de contribuintes)

from pathlib import Path
import sys
import re, unicodedata, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- bootstrap para permitir import src/*
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import PROJECT_DIR
from src.validators import assert_min_rows

CSV_DEFAULT = "data/T7_previdencia_contribuicao.csv"
FOCO_LOCAIS = ["Brasil", "Nordeste", "Rio Grande do Norte"]

# paleta coerente com o projeto (azuis)
PALETA_SERIES = {"Ocupados - Formais": "#2C6374", "Ocupados - Informais": "#7E9AA6"}
MIN_ROWS = 18

# ------------------ utilidades ------------------
def _build_year_axis():
    anos = list(range(2019, 2026))
    labels = [str(a)[-2:] for a in anos]
    return anos, labels

def _norm_periodo(s: pd.Series) -> pd.Series:
    """Normaliza '4º tri/2019' -> '2019T4' e '2º tri/2025' -> '2025T2'."""
    def f(v: str) -> str:
        v0 = str(v)
        v1 = unicodedata.normalize("NFKD", v0).replace("Â", "").replace("º", "").replace("°", "").replace(" ", "")
        m = re.search(r"([1-4])tri[\/\-]?(20\d{2})", v1, flags=re.I)
        if m:
            return f"{m.group(2)}T{m.group(1)}"
        m2 = re.search(r"(20\d{2})", v1)
        if m2:
            y = m2.group(1)
            return "2025T2" if y == "2025" else f"{y}T4"
        return v0
    return s.astype(str).map(f)

def _safe_read_csv(path_csv: str) -> pd.DataFrame:
    """Leitura robusta do CSV, aceitando ';' e vírgula decimal."""
    def read_any(p):
        try:
            return pd.read_csv(p, sep=None, engine="python", dtype=str)
        except Exception:
            return pd.read_csv(p, sep=None, engine="python", dtype=str, encoding="latin-1")

    df = read_any(path_csv)

    # Caso venha tudo em uma coluna
    if df.shape[1] == 1 and ";" in df.columns[0]:
        cols = [c.strip() for c in df.columns[0].split(";")]
        rows = []
        for raw in df.iloc[:, 0].astype(str):
            parts = [p.strip() for p in raw.split(";")]
            rows.append(parts + [""] * (len(cols) - len(parts)))
        df = pd.DataFrame(rows, columns=cols)

    lower = {c.lower(): c for c in df.columns}
    def _find(*alts):
        for a in alts:
            if a in lower:
                return lower[a]
        return None

    c_per = _find("periodo", "trimestre", "tempo", "quarter")
    c_loc = _find("local", "uf", "regiao", "região", "territorio")
    c_grp = _find("grupo", "categoria", "tipo")
    c_pct = _find("pct_contrib", "taxa", "percentual")

    missing = [n for n, c in [("periodo", c_per), ("local", c_loc), ("grupo", c_grp), ("pct_contrib", c_pct)] if c is None]
    if missing:
        raise RuntimeError(f"CSV sem colunas obrigatórias: {missing}. Colunas disponíveis: {list(df.columns)}")

    df = df.rename(columns={c_per: "periodo", c_loc: "local", c_grp: "grupo", c_pct: "pct_contrib"})
    df["periodo"] = _norm_periodo(df["periodo"])
    df["local"] = df["local"].astype(str)
    df["grupo"] = df["grupo"].astype(str)

    df["pct_contrib"] = (df["pct_contrib"].astype(str)
                         .str.replace(",", ".", regex=False))
    df["pct_contrib"] = pd.to_numeric(df["pct_contrib"], errors="coerce")

    df = df.dropna(subset=["periodo", "local", "grupo", "pct_contrib"])
    return df

def _to_uniform_series(df: pd.DataFrame) -> pd.DataFrame:
    """Seleciona T4 (<=2024) e T2 (2025) por local e grupo."""
    anos, _ = _build_year_axis()
    rows = []
    for (loc, grp), g in df.groupby(["local", "grupo"]):
        for ano in anos:
            cand = g[g["periodo"].str.startswith(str(ano))]
            if cand.empty:
                continue
            if ano <= 2024:
                t4 = cand[cand["periodo"].str.endswith("T4")]
                row = t4.iloc[0] if not t4.empty else cand.iloc[-1]
            else:
                t2 = cand[cand["periodo"].str.endswith("T2")]
                row = t2.iloc[0] if not t2.empty else cand.iloc[-1]
            rows.append({"ano": ano, "local": loc, "grupo": grp, "pct": float(row["pct_contrib"])})
    return pd.DataFrame(rows)

# ------------------ gráfico ------------------
def main(path_csv: str = CSV_DEFAULT):
    df = _safe_read_csv(path_csv)
    df = df[df["local"].isin(FOCO_LOCAIS) & df["grupo"].isin(["Ocupados - Formais", "Ocupados - Informais"])]
    assert_min_rows(df, MIN_ROWS, "taxa de contribuição previdenciária — form/informais")

    df_u = _to_uniform_series(df)
    anos, anos_lbl = _build_year_axis()
    anos_exist = sorted(df_u["ano"].unique())
    x = np.arange(len(anos_exist))
    width = 0.36

    plt.rcParams.update({
        "figure.figsize": (15.2, 7.0),
        "axes.facecolor": "white",
        "axes.grid": True, "grid.color": "#eaeaea", "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "savefig.bbox": "tight",
    })

    fig, axes = plt.subplots(1, 3, sharex=True, sharey=True)

    for ax, local in zip(axes, FOCO_LOCAIS):
        base = df_u[df_u["local"] == local]
        vals_form = [base[(base["ano"] == a) & (base["grupo"] == "Ocupados - Formais")]["pct"].mean() for a in anos_exist]
        vals_inf  = [base[(base["ano"] == a) & (base["grupo"] == "Ocupados - Informais")]["pct"].mean() for a in anos_exist]

        bars1 = ax.bar(x - width/2, vals_form, width, color=PALETA_SERIES["Ocupados - Formais"], label="Formais", zorder=2)
        bars2 = ax.bar(x + width/2, vals_inf,  width, color=PALETA_SERIES["Ocupados - Informais"], label="Informais", zorder=2)

        for bars in (bars1, bars2):
            for b in bars:
                h = b.get_height()
                if not np.isnan(h):
                    ax.annotate(f"{h:.1f}%", xy=(b.get_x() + b.get_width()/2, h),
                                xytext=(0, 3), textcoords="offset points",
                                ha="center", va="bottom", fontsize=9, weight="bold",
                                color="#222", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.6))

        ax.set_title(local, fontsize=12, loc="left",
                     bbox=dict(boxstyle="round,pad=0.25", fc="#f7f7f7", ec="#e0e0e0", lw=0.8))
        ax.set_xticks(x)
        ax.set_xticklabels([str(a)[-2:] for a in anos_exist])
        ax.set_ylabel("Taxa de contribuição (%)")

        ymax = math.ceil(max([v for v in (vals_form + vals_inf) if not np.isnan(v)]) + 5)
        ax.set_ylim(0, ymax)

    fig.legend(["Formais", "Informais"], ncol=2, loc="lower center", bbox_to_anchor=(0.5, 0.04))
    plt.subplots_adjust(bottom=0.16, top=0.90, wspace=0.08)

    outdir = PROJECT_DIR / "outputs" / "figs"
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / "14_previdencia_contribuicao.png"
    fig.savefig(outfile, dpi=150)
    print(f"Figura salva em: {outfile}")

if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv) > 1 else CSV_DEFAULT
    main(csv)
