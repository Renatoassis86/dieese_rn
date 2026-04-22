# -*- coding: utf-8 -*-
"""
Gap RN – BR por IDADE (2019–2025)
- Rótulos em: primeiro, pico (|gap| máximo) e último ano (2025)
- Rótulos finais à direita com setas, na cor da série, espaçamento 1.5 p.p.
"""

import os
import unicodedata
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

# -------------------- IO
CSV_CANDIDATES = ["data/T9_gap_RN_BR_idade.csv", "T9_gap_RN_BR_idade.csv"]
OUT_PATH = "outputs/figs/19_gap_RN_BR_idade.png"
X_MIN, X_MAX = 2019, 2025
DPI = 180

# -------------------- Paleta
PALETTE = {
    "14-24": "#2F6EB3",   # azul
    "25-39": "#2CA02C",   # verde
    "40-59": "#FF7F0E",   # laranja
    "60+":   "#8A64B3",   # roxo
}

# -------------------- Ajustes manuais (opcionais)
MANUAL_OFFSETS_FINAL = {
    # "25-39": +0.2,
    # "40-59": -0.2,
}
MANUAL_OFFSETS_MID = {
    # ("14-24","primeiro"): +0.3,
    # ("14-24","pico"): -0.2,
}

COL_SPACING = 1.5  # espaçamento vertical entre rótulos finais (p.p.)

# -------------------- Estilo
plt.rcParams.update({
    "font.size": 13,
    "axes.edgecolor": "#333",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.color": "#DDD",
})

# -------------------- Utils de leitura
def _find_csv():
    for p in CSV_CANDIDATES:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("Arquivo T9_gap_RN_BR_idade.csv não encontrado.")

def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower().strip()

def _coerce_year(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.replace("Â", "", regex=False)
    return pd.to_numeric(s.str.extract(r"(\d{4})")[0], errors="coerce")

def _to_number_br(x):
    if pd.isna(x): return pd.NA
    s = str(x).strip().replace(".", "").replace(",", ".")
    try: return float(s)
    except ValueError: return pd.NA

def read_csv_robusto(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=None, engine="python", dtype=str, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]

    per_col   = next((c for c in df.columns if any(k in _norm(c) for k in ("tri","period","ano"))), None)
    faixa_col = next((c for c in df.columns if any(k in _norm(c) for k in ("faixa","idade"))), None)
    gap_col   = next((c for c in df.columns if "gap" in _norm(c)), None)
    if not (per_col and faixa_col and gap_col):
        raise RuntimeError(f"Esperava colunas de período, idade e gap. Achei: {df.columns.tolist()}")

    df["ano"]   = _coerce_year(df[per_col])
    df["grupo"] = df[faixa_col].astype(str).str.strip()   # <-- corrigido (.str.strip())

    # normaliza nomes das faixas para bater com a paleta
    def _map_faixa(x: str) -> str:
        t = _norm(x)
        if "14" in t and "24" in t: return "14-24"
        if "25" in t and "39" in t: return "25-39"
        if "40" in t and "59" in t: return "40-59"
        if "60" in t:               return "60+"
        return x
    df["grupo"] = df["grupo"].map(_map_faixa)

    df["gap"] = df[gap_col].apply(_to_number_br)
    df = df.dropna(subset=["ano","gap"])
    df = df[(df["ano"]>=X_MIN)&(df["ano"]<=X_MAX)]
    if df.empty:
        raise RuntimeError("Planilha sem dados utilizáveis após normalização.")
    return df.sort_values(["grupo","ano"])[["ano","grupo","gap"]]

# -------------------- Rótulos auxiliares
def label_first_and_peak(ax, xs, ys, color, grupo):
    """Coloca rótulos no primeiro e no pico (|gap| máximo)."""
    if not xs: return
    idx_first = 0
    idx_peak = int(np.nanargmax(np.abs(ys))) if len(ys) else 0
    for idx, tag in [(idx_first,"primeiro"), (idx_peak,"pico")]:
        xi, yi = xs[idx], ys[idx]
        base = +0.35 if yi >= 0 else -0.35
        dy = MANUAL_OFFSETS_MID.get((grupo, tag), base)
        ax.text(xi, yi + dy, f"{yi:.1f} p.p.",
                ha="center", va="center", color=color, weight="bold",
                path_effects=[pe.withStroke(linewidth=3, foreground="white")])

def place_right_column_labels(ax, last_points, palette, x_pad=0.26, spacing=1.5):
    """
    Empilha rótulos finais (2025) à direita, com setas, mantendo a cor da série.
    last_points = [{"grupo":, "x":, "y":}, ...]
    """
    if not last_points: return
    last_points = sorted(last_points, key=lambda d: d["y"], reverse=True)
    y_anchor = last_points[0]["y"]
    for i, p in enumerate(last_points):
        grp, x_last, y_last = p["grupo"], p["x"], p["y"]
        y_label = y_anchor - i*spacing + MANUAL_OFFSETS_FINAL.get(grp, 0.0)
        color = palette.get(grp, "#333")
        # texto
        ax.text(x_last + x_pad, y_label, f"{y_last:.1f} p.p.",
                ha="left", va="center", color=color, weight="bold",
                path_effects=[pe.withStroke(linewidth=3, foreground="white")])
        # setinha ligando ponto → rótulo
        ax.annotate("", xy=(x_last + x_pad*0.65, y_label), xytext=(x_last, y_last),
                    arrowprops=dict(arrowstyle="-", color=color, lw=1.2, alpha=0.7))

# -------------------- Plot
def plot_gap(df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(12, 5), dpi=DPI)

    last_points = []

    for grupo, color in PALETTE.items():
        sub = df[df["grupo"] == grupo].sort_values("ano")
        if sub.empty: continue

        xs = sub["ano"].tolist()
        ys = sub["gap"].tolist()

        # linha contínua até 2024 + traço 2024→2025
        if len(xs) >= 2 and xs[-1] == 2025:
            ax.plot(xs[:-1], ys[:-1], color=color, lw=2.8, marker="o", label=grupo)
            ax.plot(xs[-2:], ys[-2:], color=color, lw=2.8, ls="--", marker="o")
        else:
            ax.plot(xs, ys, color=color, lw=2.8, marker="o", label=grupo)

        # destaca e guarda o último ponto
        ax.scatter([xs[-1]], [ys[-1]], s=110, facecolors=color,
                   edgecolors="white", lw=1.3, zorder=4)
        ax.scatter([xs[-1]], [ys[-1]], s=150, facecolors="none",
                   edgecolors="#6D597A", lw=1.2, zorder=4)
        last_points.append({"grupo": grupo, "x": xs[-1], "y": ys[-1]})

        # rótulos intermediários
        label_first_and_peak(ax, xs, ys, color, grupo)

    # rótulos finais à direita (sem sobrepor)
    place_right_column_labels(ax, last_points, PALETTE, x_pad=0.26, spacing=COL_SPACING)

    # eixos
    ax.set_xlim(X_MIN - 0.2, X_MAX + 1.1)   # espaço à direita para rótulos
    ax.set_xticks(range(X_MIN, X_MAX + 1))
    ax.set_ylabel("Gap RN - BR (p.p.)")
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.15), frameon=False)

    # padding vertical automático
    y_min, y_max = df["gap"].min(), df["gap"].max()
    pad = max(1.2, (y_max - y_min) * 0.18)
    ax.set_ylim(y_min - pad, y_max + pad)

    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Figura salva em: {out_path}")

# -------------------- main
def main():
    csv = _find_csv()
    df = read_csv_robusto(csv)
    plot_gap(df, OUT_PATH)

if __name__ == "__main__":
    main()
