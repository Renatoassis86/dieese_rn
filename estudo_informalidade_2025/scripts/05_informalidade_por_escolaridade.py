# -*- coding: utf-8 -*-
# scripts/05d_informalidade_por_escolaridade_barras_por_local.py
#
# Um gráfico (barras agrupadas) por LOCAL (BR, NE, RN):
# - Eixo X: ESCOLARIDADE (Fundamental, Médio, Superior). "Sem instrução" é removido se não existir.
# - Dentro de cada grupo: 7 barras (anos 2019..2025).
# - Paleta de azuis ESPECÍFICA POR LOCAL (BR, NE, RN).
# - Badge superior com o nome do LOCAL.
# - Badge colorido nos rótulos de ESCOLARIDADE.
# - Rótulos percentuais (1 casa) nas barras.
# - Validações: sem xlabel, grupos corretos e rótulos suficientes.

# --- bootstrap para permitir `import src` ---
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ------------------------------------------------

from typing import List, Tuple, Dict
import re
import unicodedata
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
LOCAIS = ["Brasil", "Nordeste", "Rio Grande do Norte"]
LOCAL_SIGLA = {"Brasil": "BR", "Nordeste": "NE", "Rio Grande do Norte": "RN"}

ESCOLAS_CANON = ["Sem instrução", "Fundamental", "Médio", "Superior"]

# Paletas por LOCAL (7 tons — 2019→2025; claro → escuro)
PALETA_ANOS_POR_LOCAL = {
    "Brasil": [
        "#B7C9E6", "#A2B9DF", "#8DA9D7", "#7899D0", "#6289C8", "#4D79C1", "#3869B9"
    ],
    "Nordeste": [
        "#B2CBD5", "#9BBFCA", "#85B3BE", "#6EA7B3", "#589BA7", "#428F9C", "#2C8390"
    ],
    "Rio Grande do Norte": [
        "#B4C3D2", "#9FB3C6", "#8AA3BA", "#7594AF", "#6084A3", "#4B7497", "#36658B"
    ],
}

# Cores do badge por ESCOLARIDADE (apenas nos rótulos do eixo X)
ESCOLARIDADE_BADGE = {
    "Sem instrução": "#9E9E9E",
    "Fundamental":   "#2A9D8F",
    "Médio":         "#457B9D",
    "Superior":      "#E9C46A",
}

CSV_DEFAULT = "data/T1d_informalidade_por_escolaridade.csv"
MIN_ROWS = 24
# ------------------------------------------------

# ----------------- utils -----------------
def _build_year_axis() -> Tuple[List[int], List[str]]:
    anos = list(range(2019, 2026))
    labels = [str(a)[-2:] for a in anos]  # '19'..'25'
    return anos, labels

def _percent_fmt(x, _pos=None):
    return f"{x:.0f}%"

def _fmt_pct_text(v: float) -> str:
    return f"{v:.1f}%".replace(".", ",")

def _norm_text(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s

def _canon_escolaridade(x: str) -> str:
    k = _norm_text(x)
    # Sem instrução (inclui "sem instrução e fundamental incompleto")
    if "sem" in k and ("instruc" in k or "instru" in k):
        return "Sem instrução"
    if "n instru" in k or "nao instru" in k:
        return "Sem instrução"
    if "fund" in k and "incomp" in k and "medio" not in k:
        return "Sem instrução"
    # Fundamental (fund completo; médio incompleto)
    if "fund" in k and "comp" in k:
        return "Fundamental"
    if "medio" in k and "incomp" in k:
        return "Fundamental"
    # Médio (médio completo; superior incompleto)
    if "medio" in k and "comp" in k:
        return "Médio"
    if "super" in k and "incomp" in k:
        return "Médio"
    # Superior (superior completo)
    if "super" in k and ("comp" in k or "completo" in k):
        return "Superior"
    # fallback por palavra-chave
    if "fund" in k:
        return "Fundamental"
    if "medio" in k:
        return "Médio"
    if "super" in k:
        return "Superior"
    return x

def _pick_annual_row(g: pd.DataFrame, ano: int) -> pd.DataFrame:
    # 2019–2024: último trimestre disponível; 2025: prioriza T2
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

def _to_uniform(df: pd.DataFrame) -> pd.DataFrame:
    anos, labels = _build_year_axis()
    rows = []
    for (esc, loc), g in df.groupby(["Escolaridade", "local"], sort=False):
        for ano in anos:
            r = _pick_annual_row(g, ano)
            if r.empty:
                continue
            rows.append({
                "Escolaridade": esc,
                "local": loc,
                "sigla": LOCAL_SIGLA.get(loc, loc),
                "ano": ano,
                "ano_lbl": str(ano)[-2:],  # '19'..'25'
                "y": float(r["tx_informalidade"].values[0]),
            })
    return pd.DataFrame(rows)

# ----------------- helpers de estilo -----------------
def _fade(hex_color: str, alpha: float):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)/255.0
    g = int(hex_color[2:4], 16)/255.0
    b = int(hex_color[4:6], 16)/255.0
    return (r, g, b, alpha)

def _apply_xtick_badges(ax, groups_order: List[str]):
    """Badge nos rótulos de escolaridade, com cor característica por grupo."""
    for t, esc in zip(ax.get_xticklabels(), groups_order):
        base = ESCOLARIDADE_BADGE.get(esc, "#F0F0F0")
        t.set_bbox(dict(
            boxstyle="round,pad=0.28,rounding_size=0.12",
            fc=_fade(base, 0.18),
            ec=_fade(base, 0.05),
            lw=0.8
        ))

# ----------------- plot por localidade -----------------
def _plot_localidade(df_u: pd.DataFrame, local: str, outdir: Path):
    anos, year_labels = _build_year_axis()
    n_years = len(anos)

    # Grupos presentes (na ordem canônica). Removemos "Sem instrução" se não existir.
    grupos_presentes = [g for g in ESCOLAS_CANON if g in df_u["Escolaridade"].unique().tolist()]
    grupos_presentes = [g for g in grupos_presentes if g != "Sem instrução"] or grupos_presentes
    if not grupos_presentes:
        raise RuntimeError(f"[{local}] Não há escolaridades com dados para 2019–2025.")

    # Paleta específica para este local
    year_colors = PALETA_ANOS_POR_LOCAL.get(local, PALETA_ANOS_POR_LOCAL["Brasil"])

    plt.rcParams.update({
        "figure.figsize": (12.4, 7.6),
        "axes.facecolor": "white",
        "axes.grid": True, "grid.color": "#eaeaea", "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "savefig.bbox": "tight",
    })
    fig, ax = plt.subplots()

    # Badge superior com o LOCAL
    fig.text(
        0.5, 0.98, f"{local}",
        ha="center", va="top", fontsize=14, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.28", fc="#F7F7F7", ec="#DDDDDD")
    )

    group_x = np.arange(len(grupos_presentes))
    group_width = 0.78
    bar_w = group_width / n_years
    offsets = np.linspace(-group_width/2 + bar_w/2, group_width/2 - bar_w/2, n_years)

    base = df_u[df_u["local"] == local]
    labels_count = 0

    for yi, ano in enumerate(anos):
        color = year_colors[yi]
        vals = []
        for esc in grupos_presentes:
            v = base[(base["ano"] == ano) & (base["Escolaridade"] == esc)]
            vals.append(float(v["y"].values[0]) if not v.empty else np.nan)

        xpos = group_x + offsets[yi]
        bars = ax.bar(
            xpos, vals,
            width=bar_w*0.96,
            color=color, edgecolor=color, linewidth=0.9,
            label=year_labels[yi],
            zorder=2
        )

        # rótulos percentuais (1 casa) acima da barra
        for b in bars:
            h = b.get_height()
            if np.isnan(h):
                continue
            ax.text(
                b.get_x() + b.get_width()/2.0,
                h + 0.8,
                _fmt_pct_text(h),
                ha="center", va="bottom",
                rotation=90, fontsize=8.4, color="#303030"
            )
            labels_count += 1

    # eixo X: escolaridades (badge colorido), sem xlabel
    ax.set_xticks(group_x)
    ax.set_xticklabels(grupos_presentes)
    _apply_xtick_badges(ax, grupos_presentes)

    ax.yaxis.set_major_formatter(FuncFormatter(_percent_fmt))
    ax.set_ylabel("Percentual (%)")

    # limites Y com folga
    all_vals = base[base["Escolaridade"].isin(grupos_presentes)]["y"].astype(float).values
    if len(all_vals) and np.isfinite(all_vals).any():
        y_min = max(0, int(np.floor(np.nanmin(all_vals) - 3)))
        y_max = min(100, int(np.ceil (np.nanmax(all_vals) + 3)))
        ax.set_ylim(y_min, y_max)

    # legenda (anos 19..25) — tons específicos deste LOCAL
    legend_handles = [Line2D([0],[0], color=year_colors[i], lw=10) for i in range(len(year_labels))]
    fig.legend(handles=legend_handles, labels=year_labels, ncol=7,
               loc="lower center", bbox_to_anchor=(0.5, 0.035))

    plt.subplots_adjust(top=0.93, bottom=0.16)

    # ----------------- validações -----------------
    if (ax.get_xlabel() or "").strip() != "":
        raise RuntimeError(f"[{local}] Remover xlabel do eixo X.")
    if labels_count < len(grupos_presentes):
        raise RuntimeError(f"[{local}] Rótulos insuficientes: {labels_count} (< {len(grupos_presentes)}).")
    xt = [t.get_text().strip() for t in ax.get_xticklabels()]
    if xt != grupos_presentes:
        raise RuntimeError(f"[{local}] Eixo X fora do padrão. Esperado {grupos_presentes}, obtido {xt}.")

    # saída
    outdir = PROJECT_DIR / "outputs" / "figs"
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / f"05d_informalidade_por_escolaridade_barras_{LOCAL_SIGLA[local]}.png"
    fig.savefig(outfile, dpi=150)
    print(f"Figura salva ({local}): {outfile}")

def main(path_csv: str = CSV_DEFAULT):
    # 1) leitura + padronização + validações
    df = read_csv_safely(path_csv)
    df = standardize_dataframe(df)

    if "periodo" not in df.columns and "trimestre" in df.columns:
        df["periodo"] = df["trimestre"]

    if "Escolaridade" not in df.columns:
        for alt in ["escolaridade", "grau_escolaridade", "instrucao"]:
            if alt in df.columns:
                df = df.rename(columns={alt: "Escolaridade"})
                break

    require_columns(df, ["periodo", "local", "Escolaridade", "tx_informalidade"])
    assert_min_rows(df, MIN_ROWS, "informalidade por escolaridade (barras por local)")
    assert_percentage_bounds(df["tx_informalidade"], "tx_informalidade")

    # 2) normalizações
    df["periodo"] = coerce_periodo(df["periodo"])
    df["_ord"] = quarter_order_key(df["periodo"])
    df["Escolaridade"] = df["Escolaridade"].map(_canon_escolaridade)
    df = df[df["local"].isin(LOCAIS)].copy()

    # 3) anual uniforme 2019..2025
    df_u = _to_uniform(df)

    # 4) gera as 3 figuras (BR, NE, RN)
    for loc in LOCAIS:
        _plot_localidade(df_u, loc, PROJECT_DIR / "outputs" / "figs")

if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv) > 1 else CSV_DEFAULT
    main(path_csv=csv)
