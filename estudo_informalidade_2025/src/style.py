# src/style.py
# -*- coding: utf-8 -*-
import matplotlib as mpl

PALETA = [
    "#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51",
    "#6D597A", "#355070", "#4D908E"
]

def apply_matplotlib_style():
    mpl.rcParams.update({
        "figure.figsize": (8.5, 5.0),
        "figure.dpi": 120,
        "axes.facecolor": "white",
        "axes.edgecolor": "#222",
        "axes.grid": True,
        "grid.color": "#ddd",
        "grid.linestyle": "-",
        "grid.linewidth": 0.6,
        "axes.titlesize": 12,
        "axes.labelsize": 10.5,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "legend.frameon": False,
        "legend.fontsize": 9.5,
        "font.size": 10.5,
        "savefig.bbox": "tight",
        "savefig.dpi": 150,
    })
    return PALETA
