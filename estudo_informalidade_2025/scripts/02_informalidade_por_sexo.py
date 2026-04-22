# scripts/02d_informalidade_por_sexo_linhas.py
# Gráfico A: 2 faixas (coluna) — Mulher (topo) | Homem (base), 3 linhas por local
# Gráfico B: Gap (Homem − Mulher) — 3 linhas (Brasil, Nordeste, RN)
# Regras:
#  - Eixo X anual uniforme 19..25 (distâncias iguais).
#  - Marcadores somente em início, pico global, vale global e último (com anel).
#  - 2025 destacado: trecho 24→25 tracejado + anel no último ponto.
#  - Sem variações desenhadas nas linhas e sem tendência nos dois gráficos.
#  - No Gráfico A, quadro-resumo no canto superior direito com Δ total (p.p.) 19→25 por local.
#  - Anti-colisão dos rótulos dos últimos pontos e dos pontos-chave.

# --- bootstrap para permitir `import src` ---
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# --------------------------------------------

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

# -------------- parâmetros de projeto --------------
FOCO_LOCAIS = ["Brasil", "Nordeste", "Rio Grande do Norte"]
SEXO_ORDER = ["Mulher", "Homem"]  # Mulher em cima
PALETA = {"Brasil": "#264653", "Nordeste": "#2A9D8F", "Rio Grande do Norte": "#E76F51"}
HIGHLIGHT_COLOR = "#6D597A"   # anel do último ponto
MIN_ROWS = 12

# -------------- utilidades de formatação --------------
def _pct(v: float) -> str:
    return f"{v:.1f}%".replace(".", ",")

def _pp(v: float) -> str:
    v = round(float(v), 1)
    s = f"{'+' if v>0 else ''}{v:.1f} p.p."
    return s.replace(".", ",")

# -------------- eixo anual uniforme 19..25 --------------
def _build_year_axis() -> Tuple[List[int], List[str]]:
    anos = list(range(2019, 2026))          # 2019..2025
    labels = [str(a)[-2:] for a in anos]    # '19'..'25'
    return anos, labels

def _pick_annual_row(g: pd.DataFrame, ano: int) -> pd.DataFrame:
    cand = g[g["periodo"].str.startswith(str(ano))]
    if cand.empty:
        return pd.DataFrame(columns=g.columns)
    if ano <= 2024:
        ordem = {"T4":4,"T3":3,"T2":2,"T1":1}
        cand["_k"] = cand["periodo"].str[-2:].map(ordem).fillna(0)
        out = cand.sort_values("_k", ascending=False).head(1).drop(columns=["_k"])
        return out
    else:
        t2 = cand[cand["periodo"].str.endswith("T2")]
        if not t2.empty:
            return t2.head(1)
        ordem = {"T4":4,"T3":3,"T2":2,"T1":1}
        cand["_k"] = cand["periodo"].str[-2:].map(ordem).fillna(0)
        out = cand.sort_values("_k", ascending=False).head(1).drop(columns=["_k"])
        return out

def _to_uniform(df: pd.DataFrame) -> pd.DataFrame:
    anos, labels = _build_year_axis()
    rows = []
    for (loc, sexo), g in df.groupby(["local","Sexo"], sort=False):
        for i, ano in enumerate(anos):
            r = _pick_annual_row(g, ano)
            if r.empty: 
                continue
            rows.append({
                "local": loc, "Sexo": sexo,
                "x_idx": i, "x_label": labels[i], "ano": ano,
                "y": float(r["tx_informalidade"].values[0])
            })
    return pd.DataFrame(rows)

# -------------- pontos-chave (início, pico, vale, último) --------------
def _key_indices(y: np.ndarray) -> List[int]:
    n = len(y)
    if n == 0: return []
    first, last = 0, n-1
    peak, trough = int(np.nanargmax(y)), int(np.nanargmin(y))
    out = []
    for i in [first, peak, trough, last]:
        if i not in out:
            out.append(i)
    return out

def _jitter_seq(n: int, base_px: int = 6) -> List[int]:
    seq = [0]
    k = 1
    while len(seq) < n:
        seq.append(base_px*k)
        if len(seq) < n: seq.append(-base_px*k)
        k += 1
    return seq[:n]

def _mark_keypoints_except_last(ax, x: np.ndarray, y: np.ndarray, color: str):
    idxs = _key_indices(y)
    idxs = [i for i in idxs if i != len(y)-1]  # último será tratado à parte
    if not idxs: 
        return
    v_offs = [0.0, 0.7, -0.7, 1.4, -1.4][:len(idxs)]
    h_offs = _jitter_seq(len(idxs), base_px=6)
    for i, dv, dh in zip(idxs, v_offs, h_offs):
        ax.scatter([x[i]], [y[i]], s=64, color=color,
                   edgecolors="white", linewidths=1.2, zorder=3)
        ax.annotate(_pct(y[i]), xy=(x[i], y[i]),
                    xytext=(dh, dv*10), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9.1, color=color, weight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.55))

# -------------- último rótulo (anti-colisão) --------------
def _bbox_overlap(b1, b2, pad=3):
    return not (b1.x1 + pad < b2.x0 or b1.x0 - pad > b2.x1 or
                b1.y1 + pad < b2.y0 or b1.y0 - pad > b2.y1)

def _place_last_labels(ax, items: List[Tuple[float,float,str,str]]):
    # offsets pensados para três séries; se aproximarem, ainda evitam colisão
    steps = [-14, 0, 14, -22, 22, -30, 30]
    renderer = ax.figure.canvas.get_renderer()
    placed = []
    # ordenar por y (baixo→alto) distribui melhor
    for x, y, color, txt in sorted(items, key=lambda t: t[1]):
        # marcador + anel
        ax.scatter([x], [y], s=78, color=color, edgecolors="white", linewidths=1.2, zorder=4)
        ax.scatter([x], [y], s=104, facecolors="none", edgecolors=HIGHLIGHT_COLOR,
                   linewidths=1.4, zorder=4)
        for dy in steps:
            ann = ax.annotate(txt, xy=(x, y), xytext=(10, dy),
                              textcoords="offset points", ha="left", va="center",
                              fontsize=9.6, color=color, weight="bold",
                              bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.55),
                              arrowprops=dict(arrowstyle="-", lw=0.8, color=color))
            plt.draw()
            bb = ann.get_window_extent(renderer=renderer)
            if not any(_bbox_overlap(bb, pr) for pr in placed):
                placed.append(bb); break
            ann.remove()

# -------------- traços (com trecho final tracejado) --------------
def _plot_series(ax, x: np.ndarray, y: np.ndarray, color: str, label: str):
    ax.plot(x[:-1], y[:-1], color=color, linewidth=2.6, marker="o", markersize=3.5,
            label=label, zorder=2)
    ax.plot(x[-2:], y[-2:], color=color, linewidth=2.6, linestyle="--",
            marker="o", markersize=3.5, zorder=2)

# -------------- quadro-resumo Δ total 19→25 --------------
def _draw_delta_box(ax, deltas: Dict[str, float], title: str = "Variação 19→25"):
    axins = ax.inset_axes([0.72, 0.78, 0.26, 0.18])  # canto superior direito
    axins.axis("off")
    axins.text(0.0, 1.05, title, fontsize=10.5, weight="bold")
    y0 = 0.75
    dy = 0.28
    for i, loc in enumerate(FOCO_LOCAIS):
        axins.text(0.0, y0 - i*dy, loc, color=PALETA[loc], fontsize=9.5, weight="bold")
        axins.text(0.98, y0 - i*dy, _pp(deltas.get(loc, np.nan)), color=PALETA[loc],
                   fontsize=9.5, weight="bold", ha="right")

# -------------- gráfico A (Mulher em cima | Homem embaixo) --------------
def plot_paineis(df_u: pd.DataFrame, outfile: Path):
    fig, axes = plt.subplots(2, 1, sharex=True, sharey=True, figsize=(14.0, 9.2))

    # eixo x uniforme
    labels = [str(a)[-2:] for a in range(2019, 2026)]
    x_grid = np.arange(len(labels))  # 0..6

    for sexo, ax in zip(SEXO_ORDER, axes):
        last_items = []
        # para o quadro-resumo
        deltas: Dict[str, float] = {}

        for loc in FOCO_LOCAIS:
            sub = df_u[(df_u["Sexo"] == sexo) & (df_u["local"] == loc)] \
                    .sort_values("x_idx")
            if sub.empty: 
                continue
            x = sub["x_idx"].to_numpy(dtype=float)
            y = sub["y"].to_numpy(dtype=float)

            _plot_series(ax, x, y, PALETA[loc], loc)
            _mark_keypoints_except_last(ax, x, y, PALETA[loc])
            last_items.append((x[-1], y[-1], PALETA[loc], _pct(y[-1])))

            # Δ total 19→25 para o quadro-resumo
            deltas[loc] = float(y[-1] - y[0])

        # eixo e limites
        ax.set_xticks(x_grid)
        ax.set_xticklabels(labels)
        ax.set_xlim(x_grid.min()-0.15, x_grid.max()+0.15)
        ax.set_ylabel("Percentual (%)")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, pos=None: f"{v:.0f}%"))
        ax.set_title(sexo, fontsize=12, loc="left", pad=4)

        # último rótulo (anti-colisão)
        _place_last_labels(ax, last_items)

        # quadro-resumo (Δ total 19→25)
        _draw_delta_box(ax, deltas)

    axes[-1].set_xlabel("Anos")

    # y-limits globais com folga
    all_vals = df_u["y"].astype(float).values
    y_min = max(0, math.floor(np.nanmin(all_vals) - 3))
    y_max = min(100, math.ceil(np.nanmax(all_vals) + 3))
    axes[0].set_ylim(y_min, y_max)

    # legenda inferior
    leg = fig.legend(handles=[Line2D([0],[0], color=PALETA[l], lw=3) for l in FOCO_LOCAIS] +
                              [Line2D([0],[0], color=HIGHLIGHT_COLOR, lw=3, ls="--")],
                     labels=FOCO_LOCAIS + ["2025"],
                     ncol=4, loc="upper center", bbox_to_anchor=(0.5, 0.04))
    for h in getattr(leg, "legendHandles", []):
        if hasattr(h, "set_linewidth"): h.set_linewidth(3.0)

    plt.subplots_adjust(bottom=0.14, top=0.94, hspace=0.10)
    fig.savefig(outfile, dpi=150)
    print(f"Figura salva em: {outfile}")

# -------------- gráfico B (gap Homem − Mulher) --------------
def plot_gap(df_u: pd.DataFrame, outfile: Path):
    fig, ax = plt.subplots(figsize=(13.2, 7.4))
    labels = [str(a)[-2:] for a in range(2019, 2026)]
    x_grid = np.arange(len(labels))

    last_items = []
    for loc in FOCO_LOCAIS:
        g = df_u[df_u["local"] == loc]
        gh = g[g["Sexo"] == "Homem"].sort_values("x_idx")
        gm = g[g["Sexo"] == "Mulher"].sort_values("x_idx")
        merged = pd.merge(gh[["x_idx","y"]].rename(columns={"y":"h"}),
                          gm[["x_idx","y"]].rename(columns={"y":"m"}),
                          on="x_idx", how="outer").sort_values("x_idx")
        x = merged["x_idx"].to_numpy(dtype=float)
        y = (merged["h"] - merged["m"]).to_numpy(dtype=float)
        if len(y) < 2: 
            continue

        _plot_series(ax, x, y, PALETA[loc], loc)
        _mark_keypoints_except_last(ax, x, y, PALETA[loc])
        last_items.append((x[-1], y[-1], PALETA[loc], _pp(y[-1]).replace(" p.p.", " p.p.")))

    ax.set_xticks(x_grid)
    ax.set_xticklabels(labels)
    ax.set_xlim(x_grid.min()-0.15, x_grid.max()+0.15)
    ax.set_xlabel("Anos")
    ax.set_ylabel("Gap (Homem − Mulher), em p.p.")
    ax.yaxis.set_major_formatter(lambda v, pos=None: f"{v:.0f} p.p.")
    _place_last_labels(ax, last_items)

    leg = ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.14))
    for h in getattr(leg, "legendHandles", []):
        if hasattr(h, "set_linewidth"): h.set_linewidth(3.0)

    plt.subplots_adjust(bottom=0.20, top=0.96)
    fig.savefig(outfile, dpi=150)
    print(f"Figura salva em: {outfile}")

# -------------- main --------------
def main():
    # leitura/validação
    df = read_csv_safely("data/T1a_informalidade_por_sexo.csv")
    df = standardize_dataframe(df)
    require_columns(df, ["periodo", "local", "Sexo", "tx_informalidade"])
    assert_min_rows(df, MIN_ROWS, "informalidade por sexo (linhas)")
    assert_percentage_bounds(df["tx_informalidade"], "tx_informalidade")

    # período → chave trimestral (para localizar últimos trimestres)
    df["periodo"] = coerce_periodo(df["periodo"])
    df["_ord"] = quarter_order_key(df["periodo"])
    df = df[df["local"].isin(FOCO_LOCAIS) & df["Sexo"].isin(["Homem","Mulher"])].copy()

    # eixo anual uniforme
    df_u = _to_uniform(df)

    # estilo
    plt.rcParams.update({
        "axes.facecolor": "white",
        "axes.grid": True, "grid.color": "#eaeaea", "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "savefig.bbox": "tight",
    })

    outdir = PROJECT_DIR / "outputs" / "figs"
    outdir.mkdir(parents=True, exist_ok=True)
    plot_paineis(df_u, outdir / "02d_informalidade_por_sexo_linhas.png")
    plot_gap(df_u, outdir / "02e_gap_sexo_linhas.png")

if __name__ == "__main__":
    main()
