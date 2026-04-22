# -*- coding: utf-8 -*-
"""
Gap RN – BR por SEXO (2019–2025) sem título no gráfico,
com rótulos do último ano (2025) em alturas diferentes para evitar overlap.
"""

import os
import unicodedata
import pandas as pd
import matplotlib.pyplot as plt

CSV_CANDIDATES = ["data/T9_gap_RN_BR_sexo.csv", "T9_gap_RN_BR_sexo.csv"]
OUT_PATH = "outputs/figs/18_gap_RN_BR_sexo.png"
X_MIN, X_MAX = 2019, 2025
DPI = 180

PALETTE = {"Homem": "#2F5DA9", "Mulher": "#E0785A"}

# deslocamentos verticais (em p.p.) APENAS para o rótulo do último ano
LAST_LABEL_OFFSET = {"Homem": +0.75, "Mulher": -0.35}

plt.rcParams.update({
    "font.size": 13,
    "axes.edgecolor": "#333",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.color": "#DDD",
})

def _find_csv():
    for p in CSV_CANDIDATES:
        if os.path.exists(p): return p
    raise FileNotFoundError("Não encontrei T9_gap_RN_BR_sexo.csv (data/ ou raiz).")

def _normalize_str(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower().strip()

def _coerce_year(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.replace("Â", "", regex=False)
    return pd.to_numeric(s.str.extract(r"(\d{4})")[0], errors="coerce")

def _to_number_br(x):
    if pd.isna(x): return pd.NA
    s = str(x).strip()
    if s == "": return pd.NA
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return pd.NA

def read_csv_robusto(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=None, engine="python", dtype=str, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    per_col  = next((c for c in df.columns if any(k in _normalize_str(c) for k in ("tri","period","ano"))), None)
    sexo_col = next((c for c in df.columns if "sexo" in _normalize_str(c)), None)
    gap_col  = next((c for c in df.columns if "gap"  in _normalize_str(c)), None)
    if not (per_col and sexo_col and gap_col):
        raise RuntimeError(f"Esperava colunas de período/sexo/gap. Achei: {df.columns.tolist()}")

    df["ano"]   = _coerce_year(df[per_col])
    df["grupo"] = df[sexo_col].astype(str).str.strip().str.title()
    df["gap"]   = df[gap_col].apply(_to_number_br)

    df = df.dropna(subset=["ano", "gap"])
    df = df[(df["ano"] >= X_MIN) & (df["ano"] <= X_MAX)]
    df = df[df["grupo"].isin(["Homem", "Mulher"])]
    if df.empty:
        raise RuntimeError("Planilha ficou vazia após normalização (verifique separador/decimais/ano).")

    return df.sort_values(["grupo", "ano"])[["ano", "grupo", "gap"]]

def _label_first_peak(ax, xs, ys, color):
    """rótulos do primeiro e do pico absoluto (|y| máximo) com anti-overlap leve"""
    import numpy as np
    if len(xs) == 0: return
    idx_first = 0
    idx_peak  = int(np.nanargmax(np.abs(ys)))
    for i in sorted({idx_first, idx_peak}):
        ax.text(xs[i], ys[i] + (0.25 if i == idx_first else 0.25),
                f"{ys[i]:.1f} p.p.", ha="center", va="bottom", color=color, weight="bold")

def _label_last(ax, x_last, y_last, grupo, color):
    """rótulo do último ano com deslocamento específico por grupo"""
    dy = LAST_LABEL_OFFSET.get(grupo, 0.0)
    ax.text(x_last, y_last + dy, f"{y_last:.1f} p.p.",
            ha="center", va="center", color=color, weight="bold")

def plot_gap(df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(12, 5), dpi=DPI)

    for grupo, color in (("Homem", PALETTE["Homem"]), ("Mulher", PALETTE["Mulher"])):
        sub = df[df["grupo"] == grupo].sort_values("ano")
        if sub.empty: continue
        xs = sub["ano"].tolist()
        ys = sub["gap"].tolist()

        # linha contínua até 2024 e tracejada 2024->2025 (se existir)
        if len(xs) >= 2 and xs[-1] == 2025:
            ax.plot(xs[:-1], ys[:-1], color=color, lw=2.8, marker="o", label=grupo)
            ax.plot(xs[-2:], ys[-2:], color=color, lw=2.8, ls="--", marker="o")
        else:
            ax.plot(xs, ys, color=color, lw=2.8, marker="o", label=grupo)

        # destaque do último ponto
        ax.scatter([xs[-1]], [ys[-1]], s=110, facecolors=color, edgecolors="white", lw=1.3, zorder=4)
        ax.scatter([xs[-1]], [ys[-1]], s=150, facecolors="none", edgecolors="#6D597A", lw=1.2, zorder=4)

        # rótulos:
        _label_first_peak(ax, xs, ys, color)     # primeiro e pico
        _label_last(ax, xs[-1], ys[-1], grupo, color)  # último com offset específico

    ax.set_xlim(X_MIN - .2, X_MAX + .2)
    ax.set_xticks(range(X_MIN, X_MAX + 1))
    ax.set_ylabel("Gap RN - BR (p.p.)")
    # >>> sem título (removido a pedido) <<<

    ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.15), frameon=False)

    # margem vertical adequada
    y_min, y_max = df["gap"].min(), df["gap"].max()
    pad = max(0.8, (y_max - y_min) * 0.15)
    ax.set_ylim(y_min - pad, y_max + pad)

    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Figura salva em: {out_path}")

def main():
    csv = _find_csv()
    df  = read_csv_robusto(csv)
    plot_gap(df, OUT_PATH)

if __name__ == "__main__":
    main()
