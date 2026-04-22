# -*- coding: utf-8 -*-
# Gráfico de barras agrupadas — Participação da FTP em Fora da Força de Trabalho (2019→2025)
# Estrutura:
# - Eixo X com 3 grupos (Brasil, Nordeste, Rio Grande do Norte)
# - Em cada grupo, 7 barras (anos 2019..2025)
# - Paletas distintas de azuis para BR/NE/RN
# - Rótulos percentuais acima das barras (1 casa decimal)
# - Legenda inferior com anos (19..25)
# - Sem título; validação automática de rótulos e ausência de xlabel

from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from typing import Tuple, List
import re, unicodedata, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D

from src.config import PROJECT_DIR
from src.validators import assert_min_rows, assert_percentage_bounds

CSV_DEFAULT = "data/T4b_forca_trabalho_potencial_e_desalento.csv"

FOCO_LOCAIS = ["Brasil", "Nordeste", "Rio Grande do Norte"]
LOCAL_SIGLA = {"Brasil": "BR", "Nordeste": "NE", "Rio Grande do Norte": "RN"}

# Paletas (tons de azul), uma para cada local — 7 tons (2019..2025)
PALETAS = {
    "Brasil": ["#A7B8CC", "#98AEC6", "#89A4BF", "#7A99B9", "#6B8FB2", "#5C84AC", "#4D7AA5"],
    "Nordeste": ["#A7D0D9", "#97C6D2", "#87BDCB", "#77B3C4", "#68AABD", "#58A0B6", "#4897AF"],
    "Rio Grande do Norte": ["#B1B5D8", "#A2A8D0", "#949BC8", "#868EBF", "#7882B7", "#6A75AF", "#5D69A7"],
}

MIN_ROWS = 18  # segurança

def _build_year_axis() -> Tuple[List[int], List[str]]:
    anos = list(range(2019, 2026))
    labels = [str(a)[-2:] for a in anos]
    return anos, labels

def _norm_periodo(s: pd.Series) -> pd.Series:
    """Normaliza '4º tri/2019' -> '2019T4'; prioriza '2025T2'."""
    def f(v: str) -> str:
        v0 = str(v)
        v1 = unicodedata.normalize("NFKD", v0).replace("Â", "").replace("º", "").replace("°", "").replace(" ", "")
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
    """Leitura robusta com auto-mapeamento e suporte a CSV 'colado' via ';'."""
    def read_any(p):
        try:
            return pd.read_csv(p, sep=None, engine="python", dtype=str)
        except Exception:
            return pd.read_csv(p, sep=None, engine="python", dtype=str, encoding="latin-1")

    df = read_any(path_csv)

    # Se veio tudo numa coluna separada por ';'
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
    # sua coluna é 'part_FTP_em_foraFT' -> lower() vira 'part_ftp_em_foraft'
    c_taxa    = find_col("part_ftp_em_foraft", "part_ftp", "ftp_percentual", "ftp_foraft")

    missing = [n for n, c in [("periodo", c_periodo), ("local", c_local), ("taxa", c_taxa)] if c is None]
    if missing:
        raise RuntimeError(f"CSV sem colunas obrigatórias: {missing}. Colunas disponíveis: {list(df.columns)}")

    df = df.rename(columns={c_periodo: "periodo", c_local: "local", c_taxa: "taxa"})
    df["periodo"] = _norm_periodo(df["periodo"])
    df["local"] = df["local"].astype(str)
    # vírgula decimal -> ponto
    df["taxa"] = pd.to_numeric(df["taxa"].astype(str).str.replace(",", ".", regex=False), errors="coerce")

    df = df.dropna(subset=["periodo", "local", "taxa"])
    return df

def _pick_annual_row(g: pd.DataFrame, ano: int) -> pd.Series:
    """Escolhe o trimestre representativo por ano: T4 (<=2024) e T2 (2025)."""
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
    """Monta tabela anual 2019..2025 por local (apenas BR/NE/RN)."""
    anos, labels = _build_year_axis()
    rows = []
    for loc, g in df.groupby("local", sort=False):
        for ano in anos:
            r = _pick_annual_row(g, ano)
            if r.empty:
                continue
            rows.append({"local": loc, "ano": ano, "ano_lbl": str(ano)[-2:], "y": float(r["taxa"])})
    out = pd.DataFrame(rows)
    out = out[out["local"].isin(FOCO_LOCAIS)].copy()
    return out

def _fmt_pct(v: float) -> str:
    return f"{v:.1f}%".replace(".", ",")

def main(path_csv: str = CSV_DEFAULT):
    # 1) leitura e sanidade
    df = _safe_read_csv(path_csv)
    df = df[df["local"].isin(FOCO_LOCAIS)].copy()
    assert_min_rows(df, MIN_ROWS, "participação da FTP em fora da FT (barras)")
    assert_percentage_bounds(df["taxa"], "part_FTP_em_foraFT")

    # 2) anual uniforme 2019..2025
    df_u = _to_uniform(df)
    anos, labels = _build_year_axis()

    # 3) estilo
    plt.rcParams.update({
        "figure.figsize": (14.6, 8.0),
        "axes.facecolor": "white",
        "axes.grid": True, "grid.color": "#eaeaea", "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "savefig.bbox": "tight",
    })
    fig, ax = plt.subplots()

    # 4) geometria das barras
    group_x = np.arange(len(FOCO_LOCAIS))       # 0,1,2
    group_width = 0.78
    bar_w = group_width / len(anos)
    offsets = np.linspace(-group_width/2 + bar_w/2, group_width/2 - bar_w/2, len(anos))

    # 5) plot por local (paletas distintas)
    for gi, loc in enumerate(FOCO_LOCAIS):
        base = df_u[df_u["local"] == loc]
        pal = PALETAS[loc]
        for yi, ano in enumerate(anos):
            v = base[base["ano"] == ano]
            val = float(v["y"].values[0]) if not v.empty else np.nan
            xpos = group_x[gi] + offsets[yi]
            color = pal[yi]
            bar = ax.bar(
                xpos, val,
                width=bar_w*0.96, color=color, edgecolor=color, linewidth=0.9, zorder=2,
                label=labels[yi] if gi == 0 else "_nolegend_"
            )[0]
            if not np.isnan(val):
                ax.text(
                    bar.get_x() + bar.get_width()/2.0,
                    val + 0.6,
                    _fmt_pct(val),
                    ha="center", va="bottom", fontsize=8.6, color="#303030"
                )

    # 6) eixos e limites
    ax.set_xticks(group_x)
    ax.set_xticklabels([LOCAL_SIGLA[l] for l in FOCO_LOCAIS])
    ax.set_ylabel("Percentual (%)")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _pos=None: f"{v:.0f}%"))
    all_vals = df_u["y"].astype(float).values
    y_min = max(0, int(math.floor(np.nanmin(all_vals) - 3)))
    y_max = min(100, int(math.ceil(np.nanmax(all_vals) + 3)))
    ax.set_ylim(y_min, y_max)

    # 7) legenda inferior (anos 19..25; usa a paleta do BR como referência visual)
    legend_handles = [Line2D([0],[0], color=PALETAS["Brasil"][i], lw=10) for i in range(len(labels))]
    fig.legend(handles=legend_handles, labels=labels, ncol=7, loc="lower center", bbox_to_anchor=(0.5, 0.04))

    plt.subplots_adjust(top=0.95, bottom=0.12)

    # 8) validação automática
    n_pct = sum(1 for t in ax.texts if "%" in t.get_text())
    if n_pct < len(FOCO_LOCAIS) * len(anos) * 0.9:
        raise RuntimeError(f"Validação falhou: rótulos com % insuficientes ({n_pct}).")
    if ax.get_xlabel():
        raise RuntimeError("Eixo X não deve ter xlabel (remover texto adicional).")

    # 9) saída
    outdir = PROJECT_DIR / "outputs" / "figs"
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / "10_participacao_FTP_foraFT.png"
    fig.savefig(outfile, dpi=150)
    print(f"Figura salva em: {outfile}")

if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv) > 1 else CSV_DEFAULT
    main(csv)
