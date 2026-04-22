# -*- coding: utf-8 -*-
# 13_horas_formais_informais.py
# Horas habituais trabalhadas — Formais x Informais (média já fornecida)
# Um gráfico por localidade (Brasil, Nordeste, Rio Grande do Norte)
# Barras agrupadas por ano (2019..2025): duas colunas por ano (Formais, Informais)

from pathlib import Path
import sys
import re, unicodedata, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# bootstrap para importar src/*
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import PROJECT_DIR
from src.validators import assert_min_rows

CSV_DEFAULT = "data/T6_horas_formais_informais.csv"
FOCO_LOCAIS = ["Brasil", "Nordeste", "Rio Grande do Norte"]

# paleta coerente com o projeto (azuis)
PALETA_SERIES = {"Formais": "#2C6374", "Informais": "#7E9AA6"}
MIN_ROWS = 18  # segurança

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
    """Leitura robusta; aceita CSV com ';' e vírgula decimal."""
    def read_any(p):
        try:
            return pd.read_csv(p, sep=None, engine="python", dtype=str)
        except Exception:
            return pd.read_csv(p, sep=None, engine="python", dtype=str, encoding="latin-1")

    df = read_any(path_csv)

    # Caso tenha sido exportado como uma única coluna separada por ';'
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
            if a in lower: return lower[a]
        return None

    c_per = _find("periodo", "trimestre", "tempo", "quarter")
    c_loc = _find("local", "uf", "regiao", "região", "territorio")
    c_grp = _find("grupo", "categoria", "tipo")
    # usamos HORAS_HAB como métrica
    c_hab = _find("horas_hab", "horashab", "horas_habituais", "media", "mean")

    missing = [n for n, c in [("periodo", c_per), ("local", c_loc), ("grupo", c_grp), ("horas_hab", c_hab)] if c is None]
    if missing:
        raise RuntimeError(f"CSV sem colunas obrigatórias: {missing}. Colunas disponíveis: {list(df.columns)}")

    df = df.rename(columns={c_per: "periodo", c_loc: "local", c_grp: "grupo", c_hab: "horas_hab"})
    df["periodo"] = _norm_periodo(df["periodo"])
    df["local"] = df["local"].astype(str)
    df["grupo"] = df["grupo"].astype(str)

    # vírgula decimal -> ponto
    df["horas_hab"] = (df["horas_hab"].astype(str)
                          .str.replace(".", "", regex=False)
                          .str.replace(",", ".", regex=False))
    df["horas_hab"] = pd.to_numeric(df["horas_hab"], errors="coerce")

    df = df.dropna(subset=["periodo", "local", "grupo", "horas_hab"])
    return df

def _to_uniform_series(df: pd.DataFrame) -> pd.DataFrame:
    """Seleciona T4 (<=2024) e T2 (2025) como ponto anual por (local, grupo)."""
    anos, _ = _build_year_axis()
    rows = []
    for (loc, grp), g in df.groupby(["local", "grupo"]):
        for ano in anos:
            cand = g[g["periodo"].str.startswith(str(ano))]
            if cand.empty: 
                continue
            if ano <= 2024:
                pref = cand[cand["periodo"].str.endswith("T4")]
                row = pref.iloc[0] if not pref.empty else cand.iloc[-1]
            else:
                pref = cand[cand["periodo"].str.endswith("T2")]
                row = pref.iloc[0] if not pref.empty else cand.iloc[-1]
            rows.append({"ano": ano, "local": loc, "grupo": grp, "horas": float(row["horas_hab"])})
    return pd.DataFrame(rows)

# ------------------ gráfico ------------------
def main(path_csv: str = CSV_DEFAULT):
    df = _safe_read_csv(path_csv)
    df = df[df["local"].isin(FOCO_LOCAIS) & df["grupo"].isin(["Formais", "Informais"])].copy()
    assert_min_rows(df, MIN_ROWS, "horas habituais trabalhadas — form/informais")

    df_u = _to_uniform_series(df)
    anos, anos_lbl = _build_year_axis()
    anos_exist = sorted(df_u["ano"].unique())
    x = np.arange(len(anos_exist))
    width = 0.36  # largura de cada barra

    # estilo
    plt.rcParams.update({
        "figure.figsize": (15.2, 7.0),
        "axes.facecolor": "white",
        "axes.grid": True, "grid.color": "#eaeaea", "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "savefig.bbox": "tight",
    })
    fig, axes = plt.subplots(1, 3, sharex=True, sharey=True)

    # para validação
    expected_bars = 0

    for ax, local in zip(axes, FOCO_LOCAIS):
        base = df_u[df_u["local"] == local]
        vals_form = [base[(base["ano"] == a) & (base["grupo"] == "Formais")]["horas"].mean() for a in anos_exist]
        vals_inf  = [base[(base["ano"] == a) & (base["grupo"] == "Informais")]["horas"].mean() for a in anos_exist]

        bars1 = ax.bar(x - width/2, vals_form, width, color=PALETA_SERIES["Formais"], label="Formais", zorder=2)
        bars2 = ax.bar(x + width/2, vals_inf,  width, color=PALETA_SERIES["Informais"], label="Informais", zorder=2)

        # rótulos (1 casa) acima das barras
        for bars in (bars1, bars2):
            for b in bars:
                h = b.get_height()
                if not np.isnan(h):
                    ax.annotate(f"{h:.1f}",
                                xy=(b.get_x() + b.get_width()/2, h),
                                xytext=(0, 3), textcoords="offset points",
                                ha="center", va="bottom", fontsize=9, weight="bold",
                                color="#222", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.6))

        ax.set_title(local, fontsize=12, loc="left",
                     bbox=dict(boxstyle="round,pad=0.25", fc="#f7f7f7", ec="#e0e0e0", lw=0.8))
        ax.set_xticks(x)
        ax.set_xticklabels([str(a)[-2:] for a in anos_exist])
        ax.set_ylabel("Horas semanais (média)")

        ymax = math.ceil(max([v for v in (vals_form + vals_inf) if not np.isnan(v)]) + 3)
        ax.set_ylim(0, max(48, ymax))  # teto mínimo 48h para robustez

        expected_bars = len([v for v in vals_form if not np.isnan(v)]) + len([v for v in vals_inf if not np.isnan(v)])

    # legenda inferior
    fig.legend(["Formais", "Informais"], ncol=2, loc="lower center", bbox_to_anchor=(0.5, 0.04))
    plt.subplots_adjust(bottom=0.16, top=0.90, wspace=0.08)

    # ---------- validações ----------
    for i, ax in enumerate(axes, start=1):
        # contagem de rótulos numéricos
        labels_here = [t.get_text() for t in ax.texts if re.match(r"^\d+\.\d$", t.get_text() or "")]
        if len(labels_here) < expected_bars:
            raise RuntimeError(f"Validação falhou no painel {i}: rótulos insuficientes ({len(labels_here)} < {expected_bars}).")
        if ax.get_xlabel():
            raise RuntimeError("Remova xlabel — apenas ticks de anos no eixo X são permitidos.")

    # saída
    outdir = PROJECT_DIR / "outputs" / "figs"
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / "13_horas_formais_informais.png"
    fig.savefig(outfile, dpi=150)
    print(f"Figura salva em: {outfile}")

if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv) > 1 else CSV_DEFAULT
    main(csv)
