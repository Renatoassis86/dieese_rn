# -*- coding: utf-8 -*-
"""
Gap RN – BR por IDADE (2019–2025)
Gera gráfico de linha mostrando a evolução do gap_pp por faixa etária.
Rótulo do último ano é colocado à direita das linhas, sem se sobrepor.
"""

import os
import unicodedata
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# Arquivos / Saída
# ------------------------------------------------------------
CSV_CANDIDATES = [
    "data/T9_gap_RN_BR_idade.csv",
    "T9_gap_RN_BR_idade.csv",
]
OUT_PATH = "outputs/figs/19_gap_RN_BR_idade.png"
X_MIN, X_MAX = 2019, 2025
DPI = 180

# Paleta
PALETTE = {
    "14-24": "#2F6EB3",   # azul
    "25-39": "#2CA02C",   # verde
    "40-59": "#FF7F0E",   # laranja
    "60+":   "#8A64B3",   # roxo
}

# ------------------------------------------------------------
# Ajustes manuais dos rótulos finais (em pontos no eixo Y)
#   > valores positivos sobem, negativos descem
#   > mude à vontade para acertar posições finas
# ------------------------------------------------------------
MANUAL_OFFSETS = {
    # "14-24": +0.0,
    # "25-39": -0.1,
    # "40-59": +0.0,
    # "60+":   +0.2,
}

# ------------------------------------------------------------
# Estilo
# ------------------------------------------------------------
plt.rcParams.update({
    "font.size": 13,
    "axes.edgecolor": "#333",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.color": "#DDD",
})

# ------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------
def _find_csv():
    for p in CSV_CANDIDATES:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("Arquivo T9_gap_RN_BR_idade.csv não encontrado.")

def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower().strip()

def _coerce_year(series: pd.Series) -> pd.Series:
    # remove "Â" se vier de planilhas com encoding estranho
    s = series.astype(str).str.replace("Â", "", regex=False)
    return pd.to_numeric(s.str.extract(r"(\d{4})")[0], errors="coerce")

def _to_number_br(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip().replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return pd.NA

def read_csv_robusto(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=None, engine="python", dtype=str, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]

    # detecta colunas (período, faixa, gap)
    per_col = next((c for c in df.columns if any(k in _norm(c) for k in ("tri", "period", "ano"))), None)
    faixa_col = next((c for c in df.columns if any(k in _norm(c) for k in ("faixa", "idade"))), None)
    gap_col = next((c for c in df.columns if "gap" in _norm(c)), None)

    if not (per_col and faixa_col and gap_col):
        raise RuntimeError(f"Esperava colunas de período, idade e gap. Achei: {df.columns.tolist()}")

    df["ano"] = _coerce_year(df[per_col])
    df["grupo"] = df[faixa_col].astype(str).str.strip()
    df["gap"] = df[gap_col].apply(_to_number_br)

    df = df.dropna(subset=["ano", "gap"])
    df = df[(df["ano"] >= X_MIN) & (df["ano"] <= X_MAX)]
    if df.empty:
        raise RuntimeError("Planilha sem dados utilizáveis após normalização.")

    # padroniza rótulos das faixas
    def _map_faixa(x: str) -> str:
        t = _norm(x)
        if "14" in t and "24" in t:
            return "14-24"
        if "25" in t and "39" in t:
            return "25-39"
        if "40" in t and "59" in t:
            return "40-59"
        if "60" in t:
            return "60+"
        return x  # fallback

    df["grupo"] = df["grupo"].map(_map_faixa)
    return df.sort_values(["grupo", "ano"])[["ano", "grupo", "gap"]]

# ------------------------------------------------------------
# Rótulo à direita do último ponto (com anti-colisão + ajuste manual)
# ------------------------------------------------------------
def label_last_right(ax, x_last, y_last, txt, used_y, manual_offset=0.0,
                     x_pad=0.15, y_min_gap=0.45, max_tries=12):
    """
    Coloca rótulo à direita do último ponto, evitando sobreposição:
      - desloca verticalmente até ficar distante pelo menos y_min_gap de outros
      - aplica 'manual_offset' no fim, para ajustes finos por série
    """
    y = y_last
    step = 0.28
    tries = 0
    # evita colisão simples com rótulos já posicionados
    while any(abs(y - uy) < y_min_gap for uy in used_y) and tries < max_tries:
        y += step if tries % 2 == 0 else -step
        step *= 1.05
        tries += 1

    # ajuste manual por série (se houver)
    y += manual_offset

    ax.text(x_last + x_pad, y, txt, ha="left", va="center", weight="bold")
    used_y.append(y)

# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------
def plot_gap(df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots(figsize=(12, 5), dpi=DPI)

    used_y_for_last = []  # guarda y dos rótulos finais para anti-colisão
    for grupo, color in PALETTE.items():
        sub = df[df["grupo"] == grupo].sort_values("ano")
        if sub.empty:
            continue

        xs = sub["ano"].tolist()
        ys = sub["gap"].tolist()

        # segmento até 2024 sólido + 2024→2025 tracejado (se houver 2025)
        if len(xs) >= 2 and xs[-1] == 2025:
            ax.plot(xs[:-1], ys[:-1], color=color, lw=2.8, marker="o", label=grupo)
            ax.plot(xs[-2:], ys[-2:], color=color, lw=2.8, ls="--", marker="o")
        else:
            ax.plot(xs, ys, color=color, lw=2.8, marker="o", label=grupo)

        # destaca último ponto
        ax.scatter([xs[-1]], [ys[-1]], s=110, facecolors=color, edgecolors="white", lw=1.3, zorder=4)
        ax.scatter([xs[-1]], [ys[-1]], s=150, facecolors="none", edgecolors="#6D597A", lw=1.2, zorder=4)

        # rótulo do último ano à direita (sem duplicar outros rótulos)
        txt = f"{ys[-1]:.1f} p.p."
        label_last_right(
            ax,
            x_last=xs[-1],
            y_last=ys[-1],
            txt=txt,
            used_y=used_y_for_last,
            manual_offset=MANUAL_OFFSETS.get(grupo, 0.0),
            x_pad=0.18,           # quão à direita do ponto
            y_min_gap=0.45,       # distância mínima entre rótulos
            max_tries=14
        )

    # eixos / limites
    ax.set_xlim(X_MIN - 0.2, X_MAX + 0.8)   # deixa espaço à direita p/ rótulos
    ax.set_xticks(range(X_MIN, X_MAX + 1))
    ax.set_ylabel("Gap RN - BR (p.p.)")
    # sem título (padrão atual)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.15), frameon=False)

    # padding vertical automático
    y_min, y_max = df["gap"].min(), df["gap"].max()
    pad = max(1.0, (y_max - y_min) * 0.15)
    ax.set_ylim(y_min - pad, y_max + pad)

    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Figura salva em: {out_path}")

# ------------------------------------------------------------
def main():
    csv = _find_csv()
    df = read_csv_robusto(csv)
    plot_gap(df, OUT_PATH)

if __name__ == "__main__":
    main()
