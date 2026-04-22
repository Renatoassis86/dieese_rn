# scripts/01_informalidade_total.py
# Gráfico (v7): Taxa de informalidade — Brasil, Nordeste e RN
# Limpo e focado + destaque de 2025 (2º Trim):
#   - Segmento 2024→2025T2 tracejado (mesma cor da série)
#   - Anel de destaque no último marcador
#   - Item extra na legenda: "2025 (2º Trim)" com traço tracejado (cor de destaque)
# Validações, anti-colisão do último rótulo, Δ p.p. relevantes e ticks customizados mantidos.

# --- bootstrap para permitir `import src` ao rodar como arquivo ---
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ------------------------------------------------------------------

from typing import List, Tuple, Dict
import math
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

# ---------- parâmetros ----------
MIN_DELTA_PP = 0.5
PALETA = ["#264653", "#2A9D8F", "#E76F51"]  # pode mudar as cores dentro da mesma paleta
HIGHLIGHT_COLOR = "#6D597A"                  # cor de destaque para 2025 (2º Trim)

# ---------- formatação ----------
def _percent_fmt(x, _pos=None):
    return f"{x:.0f}%"

def _pp_fmt(x: float) -> str:
    v = round(float(x), 1)
    if abs(v) < MIN_DELTA_PP:
        return ""
    return f"{'+' if v > 0 else ''}{v:.1f} p.p."

def _choose_offsets(n: int, base: float = 0.6) -> List[float]:
    offs = [0.0]
    k = 1
    while len(offs) < n:
        offs.append(base * k)
        if len(offs) < n:
            offs.append(-base * k)
        k += 1
    return offs[:n]

# ---------- extremos locais (exclui primeiro/último) ----------
def _indices_picos(series: pd.Series, n: int) -> List[int]:
    y = series.to_numpy(dtype=float)
    idxs = []
    for i in range(1, n-1):
        if y[i] >= y[i-1] and y[i] >= y[i+1]:
            idxs.append(i)
    seen = set()
    return [i for i in idxs if (i not in seen and not seen.add(i))]

def _indices_vales(series: pd.Series, n: int) -> List[int]:
    y = series.to_numpy(dtype=float)
    idxs = []
    for i in range(1, n-1):
        if y[i] <= y[i-1] and y[i] <= y[i+1]:
            idxs.append(i)
    seen = set()
    return [i for i in idxs if (i not in seen and not seen.add(i))]

# ---------- marcação e anotações (início/picos/vales; o "último" é tratado à parte) ----------
def _mark_special_points(ax, x_num, y, color):
    n = len(y)
    start_i = 0
    peaks = _indices_picos(pd.Series(y), n)
    troughs = _indices_vales(pd.Series(y), n)

    ordered = []
    for i in [start_i] + peaks + troughs:
        if i not in ordered:
            ordered.append(i)

    labels = [f"{y[i]:.1f}%" for i in ordered]
    offs = _choose_offsets(len(ordered), base=0.7)
    for i, txt, dy in zip(ordered, labels, offs):
        size = 68 if i == start_i else 60
        ax.scatter([x_num[i]], [y[i]], s=size, color=color,
                   edgecolors="white", linewidths=1.2, zorder=3)
        ax.text(x_num[i], y[i] + dy, txt, ha="center", va="bottom",
                fontsize=9.2, color=color, weight="bold",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.55))

def _annotate_deltas(ax, x_num, y, color):
    if len(y) < 2:
        return
    offs = _choose_offsets(len(y) - 1, base=0.5)
    for i in range(len(y) - 1):
        dy = y[i+1] - y[i]
        txt = _pp_fmt(dy)
        if not txt:
            continue
        xm = (x_num[i] + x_num[i+1]) / 2
        ym = (y[i] + y[i+1]) / 2 + offs[i]
        ax.text(xm, ym, txt, ha="center", va="center",
                fontsize=8.8, color=color, alpha=0.95,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.6))

# ---------- último ponto: anti-colisão c/ preferência abaixo + anel de destaque ----------
def _bbox_overlap_pixels(b1, b2, pad=3):
    return not (b1.x1 + pad < b2.x0 or b1.x0 - pad > b2.x1 or
                b1.y1 + pad < b2.y0 or b1.y0 - pad > b2.y1)

def _place_last_labels(ax, last_items: List[Tuple[float, float, str, str]]):
    """
    Rótulo único do último ponto de cada série.
    Preferência por ficar ABAIXO e com um anel externo na cor de destaque.
    """
    base_steps = [-12, -20, -28, -36, -44, 0, 12, 20, 28, 36, 44]
    renderer = ax.figure.canvas.get_renderer()
    placed_bboxes = []

    for x, y, color, text in sorted(last_items, key=lambda t: t[1]):  # de baixo para cima
        # marcador do último ponto (ponto + anel externo de destaque)
        ax.scatter([x], [y], s=76, color=color, edgecolors="white", linewidths=1.2, zorder=3)
        ax.scatter([x], [y], s=100, facecolors="none", edgecolors=HIGHLIGHT_COLOR,
                   linewidths=1.4, zorder=3)

        for dy in base_steps:
            ann = ax.annotate(
                text, xy=(x, y),
                xytext=(10, dy), textcoords="offset points", ha="left", va="center",
                fontsize=9.4, color=color, weight="bold",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.55),
                arrowprops=dict(arrowstyle="-", lw=0.8, color=color),
            )
            plt.draw()
            bb = ann.get_window_extent(renderer=renderer)
            collided = any(_bbox_overlap_pixels(bb, prev, pad=3) for prev in placed_bboxes)
            if not collided:
                placed_bboxes.append(bb)
                break
            ann.remove()

# ---------- ticks: 2019..2024 e 2025 (2º Trim) ----------
def _build_custom_ticks(periodos: pd.Series, ords: pd.Series) -> Tuple[List[int], List[str]]:
    """
    Ticks em: 2019, 2020, 2021, 2022, 2023, 2024 (último tri disponível de cada ano)
              e em 2025T2 (rótulo: '2025 (2º T)').
    """
    per_map: Dict[str, int] = dict(zip(periodos, ords))
    ticks, labels = [], []
    for ano in range(2019, 2024 + 1):
        candidates = [f"{ano}T4", f"{ano}T3", f"{ano}T2", f"{ano}T1"]
        pos = next((per_map[p] for p in candidates if p in per_map), None)
        if pos is not None:
            ticks.append(pos); labels.append(str(ano))
    if "2025T2" in per_map:
        ticks.append(per_map["2025T2"]); labels.append("2025 (2º T)")
    return ticks, labels

# ---------- principal ----------
def main():
    # 1) Leitura + padronização + validações
    df = read_csv_safely("data/T1_informalidade_total.csv")
    df = standardize_dataframe(df)
    require_columns(df, ["periodo", "local", "tx_informalidade"])
    assert_min_rows(df, 8, "evolução trimestral (informalidade total)")
    assert_percentage_bounds(df["tx_informalidade"], "tx_informalidade")

    # 2) Período padronizado + eixo ordenável
    df["periodo"] = coerce_periodo(df["periodo"])
    df["_ord"] = quarter_order_key(df["periodo"])
    foco = ["Brasil", "Nordeste", "Rio Grande do Norte"]
    df = df[df["local"].isin(foco)].copy().sort_values(["_ord", "local"])

    # 3) Paleta e estilo
    cor_map = {"Brasil": PALETA[0], "Nordeste": PALETA[1], "Rio Grande do Norte": PALETA[2]}
    plt.rcParams.update({
        "figure.figsize": (12.8, 6.8),
        "axes.facecolor": "white",
        "axes.grid": True,
        "grid.color": "#eaeaea",
        "grid.linewidth": 0.8,
        "legend.frameon": False,
        "savefig.bbox": "tight",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })

    fig, ax = plt.subplots()

    # 4) Linhas (sólida até o penúltimo; traço 2024→2025T2 tracejado)
    lines, labels = [], []
    last_items: List[Tuple[float, float, str, str]] = []

    for loc in foco:
        sub = df[df["local"] == loc].copy()
        x = sub["_ord"].to_numpy(dtype=float)
        y = sub["tx_informalidade"].to_numpy(dtype=float)

        # linha sólida até o penúltimo
        line_main, = ax.plot(x[:-1], y[:-1],
                             linewidth=2.6, color=cor_map[loc],
                             marker="o", markersize=3.5, label=loc, zorder=2)
        # segmento final (2024→2025T2) tracejado na mesma cor
        ax.plot(x[-2:], y[-2:], linewidth=2.6, color=cor_map[loc],
                linestyle="--", marker="o", markersize=3.5, zorder=2)

        lines.append(line_main); labels.append(loc)

        # início, picos, vales (sem o último)
        _mark_special_points(ax, x, y, cor_map[loc])
        # Δ p.p. relevantes
        _annotate_deltas(ax, x, y, cor_map[loc])
        # último (anti-colisão + anel destaque)
        last_items.append((x[-1], y[-1], cor_map[loc], f"{y[-1]:.1f}%"))

    # 5) Eixo X customizado
    ticks, tick_labels = _build_custom_ticks(df["periodo"], df["_ord"])
    ax.set_xticks(ticks); ax.set_xticklabels(tick_labels)
    plt.setp(ax.get_xticklabels(), rotation=0)
    ax.set_xlabel("Anos")
    ax.set_ylabel("Percentual (%)")
    ax.yaxis.set_major_formatter(FuncFormatter(_percent_fmt))

    # Limites Y (0–100) com folga
    yall = df["tx_informalidade"].dropna().to_numpy(dtype=float)
    y_min = max(0, math.floor(min(yall) - 3))
    y_max = min(100, math.ceil(max(yall) + 3))
    if y_min >= y_max:
        y_min, y_max = 0, 100
    ax.set_ylim(y_min, y_max)

    # 6) Últimos rótulos (anti-colisão)
    _place_last_labels(ax, last_items)

    # 7) Legenda: séries + item extra "2025 (2º Trim)" (tracejado na cor de destaque)
    extra = Line2D([0], [0], color=HIGHLIGHT_COLOR, linestyle="--", linewidth=2.6, label="2025 (2º T)")
    leg = ax.legend(handles=lines + [extra],
                    labels=labels + ["2025 (2º T)"],
                    ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    handles = getattr(leg, "legendHandles", None) or getattr(leg, "legend_handles", [])
    for h in handles:
        if hasattr(h, "set_linewidth"):
            h.set_linewidth(3.0)
    plt.subplots_adjust(bottom=0.28)

    # 8) Salvar
    outdir = PROJECT_DIR / "outputs" / "figs"
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / "01_informalidade_total.png"
    fig.savefig(outfile, dpi=150)
    print(f"Figura salva em: {outfile}")

if __name__ == "__main__":
    main()
