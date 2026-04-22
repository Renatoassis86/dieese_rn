# scripts/03b_informalidade_por_idade_barras.py
# Gráfico de colunas por FAIXA ETÁRIA (14–24, 25–39, 40–59, 60+)
# Eixo X: locais (siglas BR, NE, RN). Em cada local, um grupo de 7 colunas (anos 2019..2025).
# Ajustes: rótulos percentuais verticais em cada barra; sem hachura para 2025; sem "Locais (siglas)" no eixo X.

# --- bootstrap para permitir `import src` ---
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ------------------------------------------------

from typing import List, Tuple, Dict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D

from src.config import PROJECT_DIR
from src.io_utils import read_csv_safely
from src.schema import standardize_dataframe
from src.schema_period import coerce_periodo, quarter_order_key
from src.validators import require_columns, assert_percentage_bounds, assert_min_rows

# ----------------- parâmetros -----------------
FAIXAS = ["14–24", "25–39", "40–59", "60+"]
LOCAIS = ["Brasil", "Nordeste", "Rio Grande do Norte"]
LOCAL_SIGLA = {"Brasil": "BR", "Nordeste": "NE", "Rio Grande do Norte": "RN"}

# paleta por ano (2019..2025) — mesma família, do claro ao escuro
YEAR_COLORS = ["#90A4AE", "#7E9AA6", "#6C8F9D", "#5A8594", "#497B8B", "#3A6F80", "#2C6374"]

MIN_ROWS = 24  # segurança
# ------------------------------------------------

def _build_year_axis() -> Tuple[List[int], List[str]]:
    anos = list(range(2019, 2026))
    labels = [str(a)[-2:] for a in anos]  # '19'..'25'
    return anos, labels

def _pick_annual_row(g: pd.DataFrame, ano: int) -> pd.DataFrame:
    cand = g[g["periodo"].str.startswith(str(ano))]
    if cand.empty:
        return pd.DataFrame(columns=g.columns)
    if ano <= 2024:
        ordem = {"T4":4, "T3":3, "T2":2, "T1":1}
        cand["_k"] = cand["periodo"].str[-2:].map(ordem).fillna(0)
        return cand.sort_values("_k", ascending=False).head(1).drop(columns=["_k"])
    else:
        t2 = cand[cand["periodo"].str.endswith("T2")]
        if not t2.empty:
            return t2.head(1)
        ordem = {"T4":4, "T3":3, "T2":2, "T1":1}
        cand["_k"] = cand["periodo"].str[-2:].map(ordem).fillna(0)
        return cand.sort_values("_k", ascending=False).head(1).drop(columns=["_k"])

def _to_uniform(df: pd.DataFrame) -> pd.DataFrame:
    anos, labels = _build_year_axis()
    rows = []
    for (faixa, local), g in df.groupby(["FaixaEtaria", "local"], sort=False):
        for ano in anos:
            r = _pick_annual_row(g, ano)
            if r.empty:
                continue
            rows.append({
                "FaixaEtaria": faixa,
                "local": local,
                "sigla": LOCAL_SIGLA.get(local, local),
                "ano": ano,
                "ano_lbl": str(ano)[-2:],  # '19'..'25'
                "y": float(r["tx_informalidade"].values[0]),
            })
    return pd.DataFrame(rows)

def _percent_fmt(x, _pos=None):
    return f"{x:.0f}%"

def _fmt_pct_text(v: float) -> str:
    return f"{v:.1f}%".replace(".", ",")

def main():
    # 1) leitura + padronização + validações
    df = read_csv_safely("data/T1b_informalidade_por_idade.csv")
    df = standardize_dataframe(df)
    require_columns(df, ["periodo", "local", "FaixaEtaria", "tx_informalidade"])
    assert_min_rows(df, MIN_ROWS, "informalidade por idade (barras)")
    assert_percentage_bounds(df["tx_informalidade"], "tx_informalidade")

    # 2) período normalizado
    df["periodo"] = coerce_periodo(df["periodo"])
    df["_ord"] = quarter_order_key(df["periodo"])
    df = df[df["local"].isin(LOCAIS) & df["FaixaEtaria"].isin(FAIXAS)].copy()

    # 3) anual uniforme 2019..2025
    df_u = _to_uniform(df)

    # 4) estilo
    plt.rcParams.update({
        "figure.figsize": (14.5, 9.2),
        "axes.facecolor": "white",
        "axes.grid": True, "grid.color": "#eaeaea", "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False,
        "savefig.bbox": "tight",
    })

    fig, axes = plt.subplots(2, 2, sharey=True)
    axes = axes.ravel()

    anos, year_labels = _build_year_axis()
    n_years = len(anos)
    n_loc = len(LOCAIS)

    group_x = np.arange(n_loc)  # 0,1,2 (BR, NE, RN)
    group_width = 0.78
    bar_w = group_width / n_years
    offsets = np.linspace(-group_width/2 + bar_w/2, group_width/2 - bar_w/2, n_years)

    # 5) plota por faixa
    for ax, faixa in zip(axes, FAIXAS):
        base = df_u[df_u["FaixaEtaria"] == faixa]

        for yi, ano in enumerate(anos):
            color = YEAR_COLORS[yi]
            edgecolor = color  # 2025 sem hach e sem borda especial

            vals = []
            for loc in LOCAIS:
                v = base[(base["ano"] == ano) & (base["local"] == loc)]
                vals.append(float(v["y"].values[0]) if not v.empty else np.nan)

            xpos = group_x + offsets[yi]
            bars = ax.bar(
                xpos, vals,
                width=bar_w*0.96,
                color=color, edgecolor=edgecolor, linewidth=0.9,
                label=year_labels[yi] if faixa == FAIXAS[0] else "_nolegend_",
                zorder=2
            )

            # rótulos verticais (para cima), alinhados acima da barra
            for b in bars:
                h = b.get_height()
                if np.isnan(h):
                    continue
                ax.text(
                    b.get_x() + b.get_width()/2.0,
                    h + 0.6,  # ligeiro deslocamento acima da barra
                    _fmt_pct_text(h),
                    ha="center", va="bottom",
                    rotation=90, fontsize=8.6, color="#303030"
                )

        # eixo X: siglas dos locais (sem rótulo adicional)
        ax.set_xticks(group_x)
        ax.set_xticklabels([LOCAL_SIGLA[l] for l in LOCAIS])
        ax.set_title(faixa, loc="left", fontsize=12, pad=4)
        ax.yaxis.set_major_formatter(FuncFormatter(_percent_fmt))

    # títulos dos eixos Y apenas na coluna da esquerda
    axes[0].set_ylabel("Percentual (%)")
    axes[2].set_ylabel("Percentual (%)")

    # Y-limits globais com folga
    all_vals = df_u["y"].astype(float).values
    y_min = max(0, int(np.floor(np.nanmin(all_vals) - 3)))
    y_max = min(100, int(np.ceil (np.nanmax(all_vals) + 3)))
    for ax in axes:
        ax.set_ylim(y_min, y_max)

    # 6) legenda dos anos (19..25) — 2025 sem hachura
    legend_handles = [Line2D([0],[0], color=YEAR_COLORS[i], lw=10) for i in range(len(year_labels))]
    leg = fig.legend(handles=legend_handles, labels=year_labels,
                     ncol=7, loc="upper center", bbox_to_anchor=(0.5, 0.04))

    plt.subplots_adjust(top=0.93, bottom=0.12, wspace=0.10, hspace=0.18)

    outdir = PROJECT_DIR / "outputs" / "figs"
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / "03_informalidade_por_idade_barras.png"
    fig.savefig(outfile, dpi=150)
    print(f"Figura salva em: {outfile}")

if __name__ == "__main__":
    main()
