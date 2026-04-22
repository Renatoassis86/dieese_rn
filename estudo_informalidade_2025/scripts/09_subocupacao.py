# -*- coding: utf-8 -*-
# Gráfico de barras agrupadas — Subocupação por Local (BR, NE, RN) e Ano (2019→2025)
# - Eixo X: grupos (Brasil, Nordeste, Rio Grande do Norte)
# - Dentro de cada grupo: 7 colunas (2019..2025), com paleta de azuis distinta por local
# - Rótulos percentuais acima de cada barra (1 casa decimal)
# - Legenda inferior com anos (19..25)
# - Sem título; estilo minimalista e coerente com os gráficos anteriores (DT/ST)
# - Validação automática ao final

from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from typing import Dict, List, Tuple
import re, unicodedata, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

from src.config import PROJECT_DIR
from src.validators import assert_min_rows, assert_percentage_bounds

CSV_DEFAULT = "data/T4_subocupacao.csv"
FOCO_LOCAIS = ["Brasil", "Nordeste", "Rio Grande do Norte"]
LOCAL_SIGLA = {"Brasil": "BR", "Nordeste": "NE", "Rio Grande do Norte": "RN"}

# Paletas azuis distintas por local (7 tons para 2019..2025)
PALETAS = {
    "Brasil": [
        "#A7B8CC", "#98AEC6", "#89A4BF", "#7A99B9", "#6B8FB2", "#5C84AC", "#4D7AA5"
    ],
    "Nordeste": [
        "#A7D0D9", "#97C6D2", "#87BDCB", "#77B3C4", "#68AABD", "#58A0B6", "#4897AF"
    ],
    "Rio Grande do Norte": [
        "#B1B5D8", "#A2A8D0", "#949BC8", "#868EBF", "#7882B7", "#6A75AF", "#5D69A7"
    ],
}

MIN_ROWS = 18

def _build_year_axis() -> Tuple[List[int], List[str]]:
    anos = list(range(2019, 2026))
    labels = [str(a) for a in anos]
    return anos, labels

def _norm_periodo(s: pd.Series) -> pd.Series:
    """Normaliza '4º tri/2019' -> '2019T4'; para 2025 prioriza T2."""
    def f(v: str) -> str:
        v0 = str(v)
        v1 = unicodedata.normalize("NFKD", v0).replace("Â", "").replace("º", "").replace("°", "")
        v1 = v1.replace(" ", "")
        m = re.search(r"([1-4])tri[\/\-]?(20\d{2})", v1, flags=re.I)
        if m:
            return f"{m.group(2)}T{m.group(1)}"
        m2 = re.match(r"(20\d{2})T([1-4])$", v1)
        if m2:
            return v1
        m3 = re.search(r"(20\d{2})", v1)
        if m3:
            y = m3.group(1)
            return "2025T2" if y == "2025" else f"{y}T4"
        return v0
    return s.astype(str).map(f)

def _safe_read_csv(path_csv: str) -> pd.DataFrame:
    """Leitura robusta com auto-mapeamento de colunas e vírgula decimal."""
    def read_any(p):
        try:
            return pd.read_csv(p, sep=None, engine="python", dtype=str)
        except Exception:
            return pd.read_csv(p, sep=None, engine="python", dtype=str, encoding="latin-1")

    df = read_any(path_csv)

    # Se vier "colado" num único campo com ';'
    if df.shape[1] == 1 and ";" in df.columns[0]:
        cols = [c.strip() for c in df.columns[0].split(";")]
        rows = []
        for raw in df.iloc[:, 0].astype(str):
            parts = [p.strip() for p in raw.split(";")]
            parts += [""] * (len(cols) - len(parts))
            rows.append(parts[:len(cols)])
        df = pd.DataFrame(rows, columns=cols)

    lower = {c.lower(): c for c in df.columns}

    def find_col(*alts):
        for a in alts:
            if a in lower:
                return lower[a]
        return None

    c_periodo = find_col("periodo", "trimestre", "tempo", "quarter")
    c_local   = find_col("local", "uf", "regiao", "região", "territorio")
    c_taxa    = find_col("tx_subocup", "tx_subocupacao", "tx_subocup_%", "subocupacao", "taxa")

    missing = [n for n, c in [("periodo", c_periodo), ("local", c_local), ("taxa", c_taxa)] if c is None]
    if missing:
        raise RuntimeError(f"CSV sem colunas obrigatórias: {missing}. Colunas disponíveis: {list(df.columns)}")

    df = df.rename(columns={c_periodo: "periodo", c_local: "local", c_taxa: "taxa"})
    df["periodo"] = _norm_periodo(df["periodo"])
    df["local"] = df["local"].astype(str)
    df["taxa"] = pd.to_numeric(df["taxa"].astype(str).str.replace(",", ".", regex=False), errors="coerce")

    df = df.dropna(subset=["periodo", "local", "taxa"])
    return df

def _pick_annual_row(g: pd.DataFrame, ano: int) -> pd.Series:
    """Escolhe a observação representativa por ano (T4; em 2025 prioriza T2)."""
    cand = g[g["periodo"].str.startswith(str(ano))]
    if cand.empty:
        return pd.Series(dtype=float)
    ordem = {"T4": 4, "T3": 3, "T2": 2, "T1": 1}
    if ano <= 2024:
        cand = cand.assign(_k=cand["periodo"].str[-2:].map(ordem).fillna(0))
        return cand.sort_values("_k", ascending=False).iloc[0]
    t2 = cand[cand["periodo"].str.endswith("T2")]
    if not t2.empty:
        return t2.iloc[0]
    cand = cand.assign(_k=cand["periodo"].str[-2:].map(ordem).fillna(0))
    return cand.sort_values("_k", ascending=False).iloc[0]

def _to_uniform(df: pd.DataFrame) -> pd.DataFrame:
    """Converte a tabela para 2019..2025 anual por local."""
    anos, labels = _build_year_axis()
    rows = []
    for loc, g in df.groupby("local", sort=False):
        for i, ano in enumerate(anos):
            r = _pick_annual_row(g, ano)
            if r.empty:
                continue
            rows.append({
                "local": loc,
                "ano": ano,
                "ano_lbl": labels[i],
                "y": float(r["taxa"]),
            })
    out = pd.DataFrame(rows)
    # mantém apenas os 3 focos
    out = out[out["local"].isin(FOCO_LOCAIS)].copy()
    return out

def _fmt_pct(v: float) -> str:
    return f"{v:.1f}%".replace(".", ",")

def main(path_csv: str = CSV_DEFAULT):
    # Leitura + checagens
    df = _safe_read_csv(path_csv)
    df = df[df["local"].isin(FOCO_LOCAIS)].copy()
    assert_min_rows(df, MIN_ROWS, "subocupação (barras por local)")
    assert_percentage_bounds(df["taxa"], "tx_subocupação")

    df_u = _to_uniform(df)  # colunas: local, ano, ano_lbl, y

    # Estilo
    plt.rcParams.update({
        "figure.figsize": (14.6, 8.0),
        "axes.facecolor": "white",
        "axes.grid": True, "grid.color": "#eaeaea", "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "savefig.bbox": "tight",
    })

    fig, ax = plt.subplots()

    anos, year_labels = _build_year_axis()
    n_years = len(anos)
    group_x = np.arange(len(FOCO_LOCAIS))  # 0,1,2
    group_width = 0.78
    bar_w = group_width / n_years
    offsets = np.linspace(-group_width/2 + bar_w/2, group_width/2 - bar_w/2, n_years)

    # Plot por local
    for gi, loc in enumerate(FOCO_LOCAIS):
        base = df_u[df_u["local"] == loc]
        palette = PALETAS[loc]
        for yi, ano in enumerate(anos):
            color = palette[yi]
            v = base[base["ano"] == ano]
            val = float(v["y"].values[0]) if not v.empty else np.nan
            xpos = group_x[gi] + offsets[yi]
            bar = ax.bar(
                xpos, val, width=bar_w*0.96, color=color, edgecolor=color, linewidth=0.9, zorder=2,
                label=year_labels[yi] if (gi == 0) else "_nolegend_"
            )[0]
            if not np.isnan(val):
                ax.text(
                    bar.get_x() + bar.get_width()/2.0,
                    val + 0.6,
                    _fmt_pct(val),
                    ha="center", va="bottom",
                    rotation=0, fontsize=8.6, color="#303030"
                )

    # Eixo X: siglas dos locais
    ax.set_xticks(group_x)
    ax.set_xticklabels([LOCAL_SIGLA[l] for l in FOCO_LOCAIS])

    # Formatação Y
    ax.set_ylabel("Percentual (%)")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _pos=None: f"{v:.0f}%"))

    # Y-limits globais com folga
    all_vals = df_u["y"].astype(float).values
    y_min = max(0, int(math.floor(np.nanmin(all_vals) - 3)))
    y_max = min(100, int(math.ceil(np.nanmax(all_vals) + 3)))
    ax.set_ylim(y_min, y_max)

    # Legenda dos anos (19..25). Observação: as cores do legend referem-se ao BR;
    # para NE e RN, as paletas são tons diferentes de azul, conforme especificado.
    legend_handles = [Line2D([0], [0], color=PALETAS["Brasil"][i], lw=10) for i in range(len(year_labels))]
    leg = fig.legend(handles=legend_handles, labels=year_labels,
                     ncol=7, loc="lower center", bbox_to_anchor=(0.5, 0.04))

    plt.subplots_adjust(top=0.95, bottom=0.12)

    # Validações — rótulos e eixo X sem xlabel
    n_pct_texts = sum(1 for t in ax.texts if isinstance(t.get_text(), str) and "%" in t.get_text())
    if n_pct_texts < (len(FOCO_LOCAIS) * len(anos) * 0.9):  # flexível, mas espera ~21 rótulos
        raise RuntimeError(f"Validação falhou: rótulos com % insuficientes ({n_pct_texts}).")
    if ax.get_xlabel():
        raise RuntimeError("Remova xlabel: o eixo X não deve ter texto adicional.")

    # Saída
    outdir = PROJECT_DIR / "outputs" / "figs"
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / "09_subocupacao_barras_por_local.png"
    fig.savefig(outfile, dpi=150)
    print(f"Figura salva em: {outfile}")

if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv) > 1 else CSV_DEFAULT
    main(csv)
