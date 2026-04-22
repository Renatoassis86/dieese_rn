# -*- coding: utf-8 -*-
# scripts/06_informalidade_por_setor.py
#
# Um gráfico (barras agrupadas) por LOCAL (BR, NE, RN) para "Informalidade por Setor".
# - Eixo X: SETORES (ordem canônica; usa apenas os existentes na base).
# - Dentro de cada grupo: 7 barras (anos 2019..2025). 2019–2024 = último trimestre disponível; 2025 prioriza T2.
# - Paletas de azul ESPECÍFICAS por local (BR, NE, RN).
# - Badge superior com o nome do local + badges coloridos nos rótulos dos setores.
# - Rótulos das barras (1 casa decimal, "%"), eixo Y em percentual, sem xlabel.
# - Leitura robusta do CSV (corrige arquivos com cabeçalho colado por ';').
# - Mapeamento automático de colunas + normalização de 'local' e 'setor'.
# - Validações automáticas.
#
# Como rodar:
#   python -m scripts.06_informalidade_por_setor
# ou
#   python -m scripts.06_informalidade_por_setor data/T2_informalidade_por_setor.csv

from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from typing import List, Tuple, Dict
import re
import unicodedata
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D

from src.config import PROJECT_DIR
from src.schema_period import coerce_periodo, quarter_order_key
from src.validators import assert_percentage_bounds, assert_min_rows

CSV_DEFAULT = "data/T2_informalidade_por_setor.csv"
MIN_ROWS = 24

LOCAIS_CANON = ["Brasil", "Nordeste", "Rio Grande do Norte"]
LOCAL_SIGLA = {"Brasil": "BR", "Nordeste": "NE", "Rio Grande do Norte": "RN"}

SETORES_CANON = [
    "Agropecuária",
    "Indústria",
    "Construção",
    "Comércio",
    "Serviços",
    "Administração Pública",
]

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

SETOR_BADGE = {
    "Agropecuária":           "#8FB996",
    "Indústria":              "#9C89B8",
    "Construção":             "#E9C46A",
    "Comércio":               "#2A9D8F",
    "Serviços":               "#457B9D",
    "Administração Pública":  "#F4A261",
}

# ----------------- utilidades -----------------
def _build_year_axis() -> Tuple[List[int], List[str]]:
    anos = list(range(2019, 2026))
    labels = [str(a)[-2:] for a in anos]
    return anos, labels

def _percent_fmt(x, _pos=None):
    return f"{x:.0f}%"

def _fmt_pct_text(v: float) -> str:
    return f"{v:.1f}%".replace(".", ",")

def _norm_text(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s

def _canon_local(x: str) -> str:
    k = _norm_text(x)
    if "brasil" in k:
        return "Brasil"
    if "nordeste" in k:
        return "Nordeste"
    # normaliza várias formas de RN
    if ("rio" in k and "grande" in k and "norte" in k) or ("rn" == k):
        return "Rio Grande do Norte"
    return x

def _canon_setor(x: str) -> str:
    k = _norm_text(x)
    if ("agro" in k) or ("pecu" in k) or ("agric" in k):
        return "Agropecuária"
    if ("indust" in k) or ("transform" in k) or ("extrat" in k):
        return "Indústria"
    if "constr" in k:
        return "Construção"
    if ("comerc" in k) or ("repar" in k):
        return "Comércio"
    if "servi" in k:
        return "Serviços"
    if ("adm" in k and "publ" in k) or ("setor publico" in k) or ("adminis" in k):
        return "Administração Pública"
    return x

def _read_table_robusto(path_csv: str) -> pd.DataFrame:
    """Lê CSV com robustez, inclusive quando vem tudo em uma coluna separada por ';'."""
    df = pd.read_csv(path_csv, dtype=str)
    if df.shape[1] == 1 and ";" in df.columns[0]:
        # cabeçalho colado; separa
        colnames = [c.strip() for c in df.columns[0].split(";")]
        out = []
        for val in df.iloc[:, 0].astype(str).tolist():
            parts = [p.strip() for p in val.split(";")]
            # completa com vazio se faltar
            parts += [""] * (len(colnames) - len(parts))
            out.append(parts[:len(colnames)])
        df = pd.DataFrame(out, columns=colnames)

    # mapeia nomes de coluna
    lower_map = {c.lower(): c for c in df.columns}
    def _find(*alts):
        for a in alts:
            if a in lower_map:
                return lower_map[a]
        return None

    c_periodo = _find("periodo", "trimestre", "tempo", "period", "quarter")
    c_local   = _find("local", "uf", "regiao", "região")
    c_setor   = _find("setor", "atividade", "setor_atividade", "ramo")
    c_tx      = _find("tx_informalidade", "taxa_informalidade", "informalidade", "tx")

    missing = [n for n, c in [("periodo", c_periodo), ("local", c_local), ("Setor", c_setor), ("tx_informalidade", c_tx)] if c is None]
    if missing:
        raise RuntimeError(f"CSV sem colunas obrigatórias (após auto-mapeamento): {missing}\nColunas disponíveis: {list(df.columns)}")

    df = df.rename(columns={c_periodo: "periodo", c_local: "local", c_setor: "Setor", c_tx: "tx_informalidade"})
    return df

def _pick_annual_row(g: pd.DataFrame, ano: int) -> pd.DataFrame:
    cand = g[g["periodo"].astype(str).str.startswith(str(ano))]
    if cand.empty:
        return pd.DataFrame(columns=g.columns)
    ordem = {"T4":4, "T3":3, "T2":2, "T1":1}
    if ano <= 2024:
        cand = cand.assign(_k=cand["periodo"].astype(str).str[-2:].map(ordem).fillna(0))
        return cand.sort_values("_k", ascending=False).head(1).drop(columns=["_k"])
    t2 = cand[cand["periodo"].astype(str).str.endswith("T2")]
    if not t2.empty:
        return t2.head(1)
    cand = cand.assign(_k=cand["periodo"].astype(str).str[-2:].map(ordem).fillna(0))
    return cand.sort_values("_k", ascending=False).head(1).drop(columns=["_k"])

def _to_uniform(df: pd.DataFrame) -> pd.DataFrame:
    anos, _ = _build_year_axis()
    rows = []
    for (setor, loc), g in df.groupby(["Setor", "local"], sort=False):
        for ano in anos:
            r = _pick_annual_row(g, ano)
            if r.empty:
                continue
            rows.append({
                "Setor": setor,
                "local": loc,
                "sigla": LOCAL_SIGLA.get(loc, loc),
                "ano": ano,
                "ano_lbl": str(ano)[-2:],
                "y": float(r["tx_informalidade"]),
            })
    return pd.DataFrame(rows)

def _fade(hex_color: str, alpha: float):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)/255.0
    g = int(hex_color[2:4], 16)/255.0
    b = int(hex_color[4:6], 16)/255.0
    return (r, g, b, alpha)

def _apply_xtick_badges(ax, groups_order: List[str]):
    for t, s in zip(ax.get_xticklabels(), groups_order):
        base = SETOR_BADGE.get(s, "#F0F0F0")
        t.set_bbox(dict(
            boxstyle="round,pad=0.28,rounding_size=0.12",
            fc=_fade(base, 0.18),
            ec=_fade(base, 0.05),
            lw=0.8
        ))

# ----------------- plot -----------------
def _plot_localidade(df_u: pd.DataFrame, local: str, outdir: Path):
    anos, year_labels = _build_year_axis()
    grupos_presentes = [g for g in SETORES_CANON if g in df_u["Setor"].unique().tolist()]
    if not grupos_presentes:
        raise RuntimeError(f"[{local}] Não há setores com dados para 2019–2025.")

    year_colors = PALETA_ANOS_POR_LOCAL.get(local, PALETA_ANOS_POR_LOCAL["Brasil"])

    plt.rcParams.update({
        "figure.figsize": (13.2, 8.0),
        "axes.facecolor": "white",
        "axes.grid": True, "grid.color": "#eaeaea", "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "savefig.bbox": "tight",
    })
    fig, ax = plt.subplots()

    fig.text(0.5, 0.98, f"{local}",
             ha="center", va="top", fontsize=14, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.28", fc="#F7F7F7", ec="#DDDDDD"))

    group_x = np.arange(len(grupos_presentes))
    group_width = 0.82
    bar_w = group_width / len(anos)
    offsets = np.linspace(-group_width/2 + bar_w/2, group_width/2 - bar_w/2, len(anos))

    base = df_u[df_u["local"] == local]
    labels_count = 0

    for yi, ano in enumerate(anos):
        color = year_colors[yi]
        vals = []
        for setor in grupos_presentes:
            v = base[(base["ano"] == ano) & (base["Setor"] == setor)]
            vals.append(float(v["y"].values[0]) if not v.empty else np.nan)

        xpos = group_x + offsets[yi]
        bars = ax.bar(xpos, vals, width=bar_w*0.96, color=color, edgecolor=color, linewidth=0.9,
                      label=year_labels[yi], zorder=2)

        for b in bars:
            h = b.get_height()
            if np.isnan(h): 
                continue
            ax.text(b.get_x() + b.get_width()/2.0, h + 0.8, _fmt_pct_text(h),
                    ha="center", va="bottom", rotation=90, fontsize=8.3, color="#303030")
            labels_count += 1

    ax.set_xticks(group_x)
    ax.set_xticklabels(grupos_presentes, rotation=0)
    _apply_xtick_badges(ax, grupos_presentes)

    ax.yaxis.set_major_formatter(FuncFormatter(_percent_fmt))
    ax.set_ylabel("Percentual (%)")

    all_vals = base[base["Setor"].isin(grupos_presentes)]["y"].astype(float).values
    if len(all_vals) and np.isfinite(all_vals).any():
        y_min = max(0, int(np.floor(np.nanmin(all_vals) - 3)))
        y_max = min(100, int(np.ceil (np.nanmax(all_vals) + 3)))
        ax.set_ylim(y_min, y_max)

    legend_handles = [Line2D([0],[0], color=year_colors[i], lw=10) for i in range(len(anos))]
    fig.legend(handles=legend_handles, labels=[str(a)[-2:] for a in anos], ncol=7,
               loc="lower center", bbox_to_anchor=(0.5, 0.035))

    plt.subplots_adjust(top=0.93, bottom=0.16)

    if (ax.get_xlabel() or "").strip() != "":
        raise RuntimeError(f"[{local}] Remover xlabel do eixo X.")
    if labels_count < len(grupos_presentes):
        raise RuntimeError(f"[{local}] Rótulos insuficientes: {labels_count} (< {len(grupos_presentes)}).")
    xt = [t.get_text().strip() for t in ax.get_xticklabels()]
    if xt != grupos_presentes:
        raise RuntimeError(f"[{local}] Eixo X fora do padrão. Esperado {grupos_presentes}, obtido {xt}.")

    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / f"06_informalidade_por_setor_barras_{LOCAL_SIGLA[local]}.png"
    fig.savefig(outfile, dpi=150)
    print(f"Figura salva ({local}): {outfile}")

# ----------------- pipeline principal -----------------
def main(path_csv: str = CSV_DEFAULT):
    df = _read_table_robusto(path_csv)

    # coerções de tipo
    if "tx_informalidade" in df.columns:
        df["tx_informalidade"] = pd.to_numeric(df["tx_informalidade"], errors="coerce")

    # normalizações de conteúdo
    df["local"] = df["local"].map(_canon_local)
    df["Setor"] = df["Setor"].map(_canon_setor)

    # filtros e validações base
    df = df[df["local"].isin(LOCAIS_CANON)].copy()
    assert_min_rows(df, MIN_ROWS, "informalidade por setor (barras por local)")
    assert_percentage_bounds(df["tx_informalidade"], "tx_informalidade")

    # período normalizado
    df["periodo"] = coerce_periodo(df["periodo"].astype(str))
    df["_ord"] = quarter_order_key(df["periodo"])

    # série anual uniforme
    df_u = _to_uniform(df)
    if df_u.empty:
        raise RuntimeError("Após normalização, não há observações anuais 2019–2025 (verifique os nomes de período).")

    # plota por local
    outdir = PROJECT_DIR / "outputs" / "figs"
    for loc in LOCAIS_CANON:
        _plot_localidade(df_u, loc, outdir)

if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv) > 1 else CSV_DEFAULT
    main(path_csv=csv)
