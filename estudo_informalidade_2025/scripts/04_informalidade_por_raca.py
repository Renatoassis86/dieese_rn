# -*- coding: utf-8 -*-
# Gráfico por Raça/Cor (3 painéis: Branco, Demais Raças, Preto)
# Estrutura validada e coerente com os demais gráficos do projeto.
#
# O que este código faz:
# - Lê a base padronizada (read_csv_safely + standardize_dataframe).
# - Garante colunas: periodo/local/Raca/tx_informalidade; aceita 'trimestre' como periodo.
# - Normaliza período (coerce_periodo, quarter_order_key).
# - Uniformiza série anual 2019..2025 (2019–2024: último trimestre; 2025: T2 se existir).
# - Plota 3 painéis (Branco, Demais Raças, Preto) com linhas BR/NE/RN.
# - Marcadores e rótulos (com 1 casa decimal e “%”) em: primeiro, pico, vale e último.
# - Rótulos ficam abaixo da linha; EXCEÇÃO: painel “Preto”/“Rio Grande do Norte”
#   no ÚLTIMO ponto fica ACIMA (melhor legibilidade).
# - 2024→2025 tracejado, último ponto com anel (HIGHLIGHT_COLOR).
# - Box “Variação 19→25 (p.p.)” em cada painel.
# - Legenda inferior (4 colunas).
# - Eixos: X com rótulos 19..25 (sem “Anos”), Y em Percentual (%).
#
# Como usar:
#   python -m scripts.04_informalidade_por_raca
#   # ou
#   python -m scripts.04_informalidade_por_raca data\T1c_informalidade_por_raca.csv

# --- bootstrap para permitir `import src` ---
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ------------------------------------------------

from typing import List, Tuple, Dict
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

from src.config import PROJECT_DIR
from src.io_utils import read_csv_safely
from src.schema import standardize_dataframe
from src.schema_period import coerce_periodo, quarter_order_key
from src.validators import require_columns, assert_percentage_bounds, assert_min_rows

# ----------------- parâmetros e paleta -----------------
FOCO_LOCAIS = ["Brasil", "Nordeste", "Rio Grande do Norte"]
SIGLA = {"Brasil": "BR", "Nordeste": "NE", "Rio Grande do Norte": "RN"}
RACAS = ["Branco", "Demais Raças", "Preto"]

PALETA = {"Brasil": "#264653", "Nordeste": "#2A9D8F", "Rio Grande do Norte": "#E76F51"}
HIGHLIGHT_COLOR = "#6D597A"

MIN_ROWS = 18
CSV_DEFAULT = "data/T1c_informalidade_por_raca.csv"
# -------------------------------------------------------

def _pct(v: float) -> str:
    return f"{float(v):.1f}%".replace(".", ",")

def _pp(v: float) -> str:
    v = round(float(v), 1)
    return (f"{'+' if v>0 else ''}{v:.1f} p.p.").replace(".", ",")

def _build_year_axis() -> Tuple[List[int], List[str]]:
    anos = list(range(2019, 2026))
    labels = [str(a)[-2:] for a in anos]
    return anos, labels

def _pick_annual_row(g: pd.DataFrame, ano: int) -> pd.DataFrame:
    cand = g[g["periodo"].str.startswith(str(ano))]
    if cand.empty:
        return pd.DataFrame(columns=g.columns)
    ordem = {"T4": 4, "T3": 3, "T2": 2, "T1": 1}
    if ano <= 2024:
        cand = cand.assign(_k=cand["periodo"].str[-2:].map(ordem).fillna(0))
        return cand.sort_values("_k", ascending=False).head(1).drop(columns=["_k"])
    t2 = cand[cand["periodo"].str.endswith("T2")]
    if not t2.empty:
        return t2.head(1)
    cand = cand.assign(_k=cand["periodo"].str[-2:].map(ordem).fillna(0))
    return cand.sort_values("_k", ascending=False).head(1).drop(columns=["_k"])

def _to_uniform_series(df: pd.DataFrame) -> pd.DataFrame:
    anos, labels = _build_year_axis()
    rows = []
    for (raca, local), g in df.groupby(["Raca", "local"], sort=False):
        for i, ano in enumerate(anos):
            r = _pick_annual_row(g, ano)
            if r.empty:
                continue
            rows.append({
                "Raca": raca,
                "local": local,
                "x_idx": i,
                "x_label": labels[i],
                "ano": ano,
                "y": float(r["tx_informalidade"].values[0]),
            })
    out = pd.DataFrame(rows)
    if out.empty:
        raise RuntimeError("Sem dados válidos após normalização (nenhum ponto anual composto).")
    return out[(out["local"].isin(FOCO_LOCAIS)) & (out["Raca"].isin(RACAS))].copy()

# ----------------- marcações e desenho -----------------
def _key_indices(y: np.ndarray) -> List[int]:
    if len(y) == 0:
        return []
    first, last = 0, len(y) - 1
    peak, trough = int(np.nanargmax(y)), int(np.nanargmin(y))
    out: List[int] = []
    for i in [first, peak, trough, last]:
        if i not in out:
            out.append(i)
    return out

def _jitter_seq(n: int, base_px: int = 6) -> List[int]:
    seq = [0]; k = 1
    while len(seq) < n:
        seq.append(base_px * k)
        if len(seq) < n: seq.append(-base_px * k)
        k += 1
    return seq[:n]

def _draw_key_markers(ax, x: np.ndarray, y: np.ndarray, color: str,
                      raca: str, loc: str):
    """
    Marca 1º, pico, vale e último ponto.
    Posição-padrão: rótulos ABAIXO da linha (va='top').
    Exceção: painel 'Preto' + local 'Rio Grande do Norte' → ÚLTIMO rótulo ACIMA (va='bottom').
    """
    idxs = _key_indices(y)
    if not idxs:
        return
    v_offs = [0.0, -0.8, -1.2, -0.6, -1.5][:len(idxs)]  # negativos = abaixo
    h_offs = _jitter_seq(len(idxs), base_px=5)

    for i, dv, dh in zip(idxs, v_offs, h_offs):
        # Caso especial (somente último ponto do RN em “Preto”)
        if (raca == "Preto") and (loc == "Rio Grande do Norte") and (i == len(y) - 1):
            dv = abs(dv) * 1.2   # desloca para cima
            va = "bottom"        # rótulo acima da linha
        else:
            va = "top"           # rótulo abaixo da linha

        # marcador do ponto-chave
        ax.scatter([x[i]], [y[i]], s=60, color=color,
                   edgecolors="white", linewidths=1.0, zorder=3)

        # rótulo (1 casa decimal + “%”)
        ax.annotate(
            _pct(y[i]), xy=(x[i], y[i]),
            xytext=(dh, dv * 10), textcoords="offset points",
            ha="center", va=va,
            fontsize=8.6, color=color, weight="bold",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.55),
        )

def _plot_series(ax, x: np.ndarray, y: np.ndarray, color: str):
    ax.plot(x[:-1], y[:-1], color=color, linewidth=2.3, marker="o", markersize=3.4, zorder=2)
    ax.plot(x[-2:], y[-2:], color=color, linewidth=2.3, linestyle="--", marker="o", markersize=3.4, zorder=2)

def _mark_last_point(ax, x_last: float, y_last: float, color: str):
    ax.scatter([x_last], [y_last], s=74, color=color,
               edgecolors="white", linewidths=1.0, zorder=4)
    ax.scatter([x_last], [y_last], s=100, facecolors="none",
               edgecolors=HIGHLIGHT_COLOR, linewidths=1.3, zorder=4)

def _draw_delta_box(ax, deltas: Dict[str, float], title: str = "Variação 19→25"):
    axins = ax.inset_axes([0.56, 0.70, 0.42, 0.22])
    axins.axis("off")
    axins.text(0.0, 1.02, title, fontsize=10.0, weight="bold")
    y0, dy = 0.80, 0.22
    for i, loc in enumerate(FOCO_LOCAIS):
        axins.text(0.00, y0 - i * dy, SIGLA[loc], color=PALETA[loc], fontsize=8.4, weight="bold")
        axins.text(0.98, y0 - i * dy, _pp(deltas.get(loc, np.nan)),
                   color=PALETA[loc], fontsize=8.4, weight="bold", ha="right")

# ----------------- pipeline principal -----------------
def main(path_csv: str = CSV_DEFAULT):
    # 1) leitura + padronização + validações
    df = read_csv_safely(path_csv)
    df = standardize_dataframe(df)
    if "periodo" not in df.columns and "trimestre" in df.columns:
        df["periodo"] = df["trimestre"]
    require_columns(df, ["periodo", "local", "Raca", "tx_informalidade"])
    assert_min_rows(df, MIN_ROWS, "informalidade por raça (linhas)")
    assert_percentage_bounds(df["tx_informalidade"], "tx_informalidade")

    df["periodo"] = coerce_periodo(df["periodo"])
    df["_ord"] = quarter_order_key(df["periodo"])
    df = df[df["local"].isin(FOCO_LOCAIS) & df["Raca"].isin(RACAS)].copy()
    df_u = _to_uniform_series(df)

    plt.rcParams.update({
        "figure.figsize": (15.2, 6.9),
        "axes.facecolor": "white",
        "axes.grid": True, "grid.color": "#eaeaea", "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "savefig.bbox": "tight",
        "font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
        "legend.fontsize": 9.6, "xtick.labelsize": 10, "ytick.labelsize": 10,
    })

    fig, axes = plt.subplots(1, 3, sharex=True, sharey=True)
    _, labels = _build_year_axis()
    x_grid = np.arange(len(labels))

    for ax_idx, (ax, raca) in enumerate(zip(axes, RACAS)):
        deltas: Dict[str, float] = {}

        for loc in FOCO_LOCAIS:
            sub = df_u[(df_u["Raca"] == raca) & (df_u["local"] == loc)].sort_values("x_idx")
            if sub.empty:
                continue
            x = sub["x_idx"].to_numpy(float)
            y = sub["y"].to_numpy(float)
            _plot_series(ax, x, y, PALETA[loc])
            _draw_key_markers(ax, x, y, PALETA[loc], raca=raca, loc=loc)  # ← aplica exceção Preto/RN
            _mark_last_point(ax, x[-1], y[-1], PALETA[loc])
            deltas[loc] = float(y[-1] - y[0])

        # Título destacado
        ax.set_title(raca, fontsize=13.2, fontweight="bold", loc="left", pad=4,
                     bbox=dict(boxstyle="round,pad=0.25", fc="#f7f7f7", ec="#dddddd"))

        # Eixos
        ax.set_xticks(x_grid)
        ax.set_xticklabels(labels)
        ax.set_xlim(x_grid.min() - 0.15, x_grid.max() + 0.15)
        if ax_idx == 0:
            ax.set_ylabel("Percentual (%)")
        else:
            ax.set_ylabel("")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, pos=None: f"{v:.0f}%"))

        # Box variação 19→25
        _draw_delta_box(ax, deltas, title="Variação 19→25")

    # Limites do eixo Y
    all_vals = df_u["y"].astype(float).values
    y_min = max(0, math.floor(np.nanmin(all_vals) - 3))
    y_max = min(100, math.ceil(np.nanmax(all_vals) + 3))
    for ax in axes:
        ax.set_ylim(y_min, y_max)

    # Legenda inferior
    leg = fig.legend(
        handles=[Line2D([0], [0], color=PALETA[l], lw=3) for l in FOCO_LOCAIS] +
                [Line2D([0], [0], color=HIGHLIGHT_COLOR, lw=3, ls="--")],
        labels=FOCO_LOCAIS + ["2025"],
        ncol=4, loc="lower center", bbox_to_anchor=(0.5, -0.02),
        handlelength=2.6, handletextpad=0.6, columnspacing=1.2, borderaxespad=0.6
    )
    for h in getattr(leg, "legendHandles", []):
        if hasattr(h, "set_linewidth"):
            h.set_linewidth(3.0)

    plt.subplots_adjust(bottom=0.14, top=0.93, wspace=0.06)

    # Saída
    outdir = PROJECT_DIR / "outputs" / "figs"
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / "04_informalidade_por_raca_linhas.png"
    plt.savefig(outfile, dpi=150)
    print(f"Figura salva em: {outfile}")

if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv) > 1 else CSV_DEFAULT
    main(path_csv=csv)
