# src/viz_utils.py
from __future__ import annotations
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import pandas as pd

def percent_formatter(ndec: int = 0):
    factor = 100.0
    fmt = f"%.{ndec}f%%"
    def _f(x, pos=None):
        if pd.isna(x):
            return ""
        return fmt % (x * factor)
    return FuncFormatter(_f)

def add_highlight_band(ax, start: pd.Timestamp, end: pd.Timestamp, alpha: float = 0.12, label: str = "Pandemia 2020–2021"):
    ax.axvspan(start, end, color="#9e9e9e", alpha=alpha, lw=0, label=label)

def label_last_points(ax, df: pd.DataFrame, x_col: str, y_col: str, group_col: str, fmt="{:.1%}", dx=5, dy=0):
    # supõe que df já está ordenado por x_col
    last = (df.sort_values(x_col)
              .groupby(group_col, as_index=False)
              .tail(1))
    for _, r in last.iterrows():
        ax.annotate(f"{r[group_col]}  {fmt.format(r[y_col])}",
                    xy=(r[x_col], r[y_col]),
                    xytext=(dx, dy),
                    textcoords="offset points",
                    ha="left", va="center",
                    fontsize=9, color=ax.lines[-1].get_color() if ax.lines else "black")

def title_block(ax, title: str, subtitle: str = "", note: str = ""):
    ax.set_title(title, loc="left", fontsize=14, weight="bold", pad=12)
    if subtitle:
        ax.text(0.0, 1.02, subtitle, transform=ax.transAxes, ha="left", va="bottom", fontsize=10, color="#555555")
    if note:
        ax.text(0.0, -0.18, note, transform=ax.transAxes, ha="left", va="top", fontsize=8, color="#6a6a6a")

def palette_br_ne_rn():
    # Paleta canônica (pode variar mantendo a hierarquia)
    return {
        "Brasil": "#1f77b4",          # azul referência
        "Nordeste": "#6baed6",        # variação mais clara
        "Rio Grande do Norte": "#d62728",  # destaque RN
    }

def apply_grid_style(ax):
    ax.grid(True, which="major", axis="y", alpha=0.15)
    ax.set_axisbelow(True)
    for spine in ["top","right"]:
        ax.spines[spine].set_visible(False)
