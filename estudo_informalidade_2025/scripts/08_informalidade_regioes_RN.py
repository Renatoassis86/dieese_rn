# -*- coding: utf-8 -*-
# scripts/08_informalidade_regioes_RN.py
#
# Informalidade por REGIÕES do RN em BARRAS AGRUPADAS por ANO:
# 2019–2024 (4º tri de cada ano) e 2025 (2º tri).
# Saída (inalterada): outputs/figs/08_informalidade_regioes_RN_trimestres.png

from pathlib import Path
import sys
import re, unicodedata
from typing import List, Dict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D

# bootstrap do projeto
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import PROJECT_DIR
from src.validators import assert_percentage_bounds, assert_min_rows

CSV_DEFAULT = "data/T3_informalidade_regioes_RN.csv"
MIN_ROWS = 12

# Paleta sequencial p/ 7 anos (mantida)
PALETTE_YEARS = ["#B7C9E6", "#A9C0E3", "#9BB7DF", "#8EAEDD", "#80A5DA", "#739CD6", "#588ACF"]

# Ordem preferencial de regiões (mantida)
REGIOES_CANON = ["Oeste", "Central", "Agreste", "Natal", "Entorno Metropolitano de Natal"]

REGIAO_BADGE = {
    "Oeste": "#F4A261",
    "Central": "#2A9D8F",
    "Agreste": "#457B9D",
    "Natal": "#6D597A",
    "Entorno Metropolitano de Natal": "#8FB996",
}

# --- utilidades (mantidas) ---
def _percent_fmt(x, _pos=None): return f"{x:.0f}%"
def _fmt_pct_text(v: float) -> str: return f"{v:.1f}%".replace(".", ",")
def _fade(hex_color: str, alpha: float):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)/255.0; g = int(hex_color[2:4], 16)/255.0; b = int(hex_color[4:6], 16)/255.0
    return (r, g, b, alpha)
def _norm_text(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii","ignore").decode("ascii")
    return re.sub(r"\s+"," ", s).strip().lower()
def _canon_regiao(x: str) -> str:
    k = _norm_text(x)
    if "entorno" in k and "natal" in k: return "Entorno Metropolitano de Natal"
    if "natal" in k: return "Natal"
    if "oeste" in k: return "Oeste"
    if "central" in k: return "Central"
    if "agreste" in k: return "Agreste"
    return str(x).strip().title()
def _normalize_periodo_series(s: pd.Series) -> pd.Series:
    # '4º tri/2019' → '2019T4'; '2º tri/2025' → '2025T2'; '2021' → '2021T4' (2025→T2)
    def _one(v: str) -> str:
        if v is None: return ""
        v1 = unicodedata.normalize("NFKD", str(v)).replace("Â","").replace("º","").replace("°","").replace(" ","")
        m = re.search(r"([1-4])tri[\/\-]?(20\d{2})", v1, flags=re.I)
        if m: return f"{m.group(2)}T{m.group(1)}"
        if re.match(r"(20\d{2})T[1-4]$", v1): return v1
        m2 = re.search(r"(20\d{2})", v1)
        if m2:
            y = m2.group(1)
            return f"{y}T2" if y=="2025" else f"{y}T4"
        return str(v)
    return s.astype(str).map(_one)

def _read_csv_smart(path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(path, sep=None, engine="python", dtype=str)
    except Exception:
        return pd.read_csv(path, sep=None, engine="python", dtype=str, encoding="latin-1")

def _read_table(path_csv: str) -> pd.DataFrame:
    df = _read_csv_smart(path_csv)
    if df.shape[1] == 1 and ";" in df.columns[0]:
        cols = [c.strip() for c in df.columns[0].split(";")]
        rows = []
        for raw in df.iloc[:,0].astype(str):
            parts = [p.strip() for p in raw.split(";")] + [""]
            rows.append(parts[:len(cols)])
        df = pd.DataFrame(rows, columns=cols)
    lower = {c.lower(): c for c in df.columns}
    def _find(*alts):
        for a in alts:
            if a in lower: return lower[a]
        return None
    c_periodo = _find("periodo","trimestre","tempo","period","quarter")
    c_local   = _find("regiao","região","local","area","territorio","território")
    c_tx      = _find("tx_informalidade","taxa_informalidade","informalidade","tx")
    if not all([c_periodo,c_local,c_tx]):
        raise RuntimeError(f"CSV sem colunas essenciais. Colunas: {list(df.columns)}")
    df = df.rename(columns={c_periodo:"periodo", c_local:"local", c_tx:"tx_informalidade"})
    df["periodo"] = _normalize_periodo_series(df["periodo"])
    df["tx_informalidade"] = pd.to_numeric(df["tx_informalidade"].astype(str).str.replace(",",".", regex=False), errors="coerce")
    df["regiao"] = df["local"].map(_canon_regiao)
    return df.dropna(subset=["tx_informalidade","regiao","periodo"])

def _apply_xtick_badges(ax, groups_order: List[str]):
    fallback = ["#8FB996","#9C89B8","#E9C46A","#2A9D8F","#457B9D","#F4A261","#90A4AE"]
    fidx = 0
    for t, reg in zip(ax.get_xticklabels(), groups_order):
        base = REGIAO_BADGE.get(reg, fallback[fidx % len(fallback)])
        if reg not in REGIAO_BADGE: fidx += 1
        t.set_bbox(dict(boxstyle="round,pad=0.28,rounding_size=0.12",
                        fc=_fade(base,0.18), ec=_fade(base,0.05), lw=0.8))

# Mapeamento fixo do relatório
TARGET_PERIODS: Dict[str,str] = {
    "2019T4":"2019",
    "2020T4":"2020",
    "2021T4":"2021",
    "2022T4":"2022",
    "2023T4":"2023",
    "2024T4":"2024",
    "2025T2":"2025 (2º T)",
}
TARGET_ORDER = list(TARGET_PERIODS.keys())

def main(path_csv: str = CSV_DEFAULT):
    df = _read_table(path_csv)
    assert_min_rows(df, MIN_ROWS, "informalidade por regiões do RN (barras anuais)")
    assert_percentage_bounds(df["tx_informalidade"], "tx_informalidade")

    # filtra só os períodos do relatório
    df = df[df["periodo"].isin(TARGET_ORDER)].copy()
    if df.empty:
        raise RuntimeError("Base não contém 2019T4–2024T4 e 2025T2 em 'periodo'.")

    # ordem de regiões (mantida)
    regs = df["regiao"].unique().tolist()
    canon = [r for r in REGIOES_CANON if r in regs]
    others = sorted([r for r in regs if r not in canon])
    grupos = canon + others
    if not grupos:
        raise RuntimeError("Nenhuma região reconhecida.")

    # pivô região × período (primeiro valor)
    df["periodo_ord"] = pd.Categorical(df["periodo"], categories=TARGET_ORDER, ordered=True)
    piv = (df.pivot_table(index="regiao", columns="periodo_ord",
                          values="tx_informalidade", aggfunc="first")
             .reindex(index=grupos, columns=TARGET_ORDER))

    # estilo igual ao projeto
    plt.rcParams.update({
        "figure.figsize": (13.6, 8.2),
        "axes.facecolor": "white",
        "axes.grid": True, "grid.color": "#eaeaea", "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "savefig.bbox": "tight",
    })
    fig, ax = plt.subplots()

    # barras por ano (mantido)
    x = np.arange(len(grupos))
    k = len(TARGET_ORDER)
    colors = PALETTE_YEARS[:k]
    group_w = 0.86
    bar_w = group_w / k
    offsets = np.linspace(-group_w/2 + bar_w/2, group_w/2 - bar_w/2, k)

    labels_count = 0
    for i, per in enumerate(TARGET_ORDER):
        vals = piv[per].values.astype(float)
        xpos = x + offsets[i]
        bars = ax.bar(xpos, vals, width=bar_w*0.96,
                      color=colors[i], edgecolor=colors[i], linewidth=0.9,
                      label=TARGET_PERIODS[per], zorder=2)
        for b in bars:
            h = b.get_height()
            if np.isnan(h): continue
            ax.text(b.get_x()+b.get_width()/2.0, h+0.8, _fmt_pct_text(h),
                    ha="center", va="bottom", rotation=90, fontsize=8.4, color="#303030")
            labels_count += 1

    ax.set_xticks(x); ax.set_xticklabels(grupos); _apply_xtick_badges(ax, grupos)
    ax.yaxis.set_major_formatter(FuncFormatter(_percent_fmt))
    ax.set_ylabel("Percentual (%)")

    all_vals = piv.values.flatten(); all_vals = all_vals[np.isfinite(all_vals)]
    if all_vals.size:
        ax.set_ylim(max(0, int(np.floor(all_vals.min()-3))),
                    min(100, int(np.ceil(all_vals.max()+3))))

    # legenda na ordem cronológica (mantida)
    handles = [Line2D([0],[0], color=colors[i], lw=10) for i in range(k)]
    labels  = [TARGET_PERIODS[p] for p in TARGET_ORDER]
    fig.legend(handles=handles, labels=labels, ncol=min(k,7),
               loc="lower center", bbox_to_anchor=(0.5, 0.035))

    plt.subplots_adjust(top=0.93, bottom=0.16)

    # checagens
    if (ax.get_xlabel() or "").strip() != "": raise RuntimeError("Remover xlabel do eixo X.")
    if labels_count < len(grupos): raise RuntimeError(f"Rótulos insuficientes: {labels_count} (< {len(grupos)}).")

    # saída (inalterada)
    outdir = PROJECT_DIR / "outputs" / "figs"
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / "08_informalidade_regioes_RN_trimestres.png"
    fig.savefig(outfile, dpi=150)
    plt.close(fig)
    print(f"Figura salva: {outfile}")

if __name__ == "__main__":
    main(CSV_DEFAULT)
