# -*- coding: utf-8 -*-
# Renda média (deflacionada) — Formais x Informais
# Ajuste final:
#   - Rótulos dos Informais do NORDESTE e do RN ficam ACIMA da linha.
#   - Todos os demais rótulos (Formais em todos os painéis e Informais do Brasil) ficam ABAIXO.
#   - Anticolisão por construção (acima vs abaixo) + margens extras de eixo.
# Saída: outputs/figs/12_renda_formais_informais.png

from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from typing import List, Tuple
import re, unicodedata, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D

from src.config import PROJECT_DIR
from src.validators import assert_min_rows

CSV_DEFAULT = "data/T5_renda_formais_informais_deflacionada.csv"

FOCO_LOCAIS = ["Brasil", "Nordeste", "Rio Grande do Norte"]
HIGHLIGHT_COLOR = "#6D597A"
PALETA_SERIES = {"Formais": "#2C6374", "Informais": "#7E9AA6"}  # família de azuis
MIN_ROWS = 18

# ----------------- utilidades -----------------
def _build_year_axis() -> Tuple[List[int], List[str]]:
    anos = list(range(2019, 2026))
    labels = [str(a)[-2:] for a in anos]
    return anos, labels

def _norm_periodo(s: pd.Series) -> pd.Series:
    """Normaliza '4º tri/2019' -> '2019T4'; se vier apenas ano: 2025->2025T2; demais->T4."""
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
    """Leitura robusta; aceita CSV 'colado' com ';' e vírgula decimal."""
    def read_any(p):
        try:
            return pd.read_csv(p, sep=None, engine="python", dtype=str)
        except Exception:
            return pd.read_csv(p, sep=None, engine="python", dtype=str, encoding="latin-1")
    df = read_any(path_csv)

    # Caso tudo venha numa única coluna separada por ';'
    if df.shape[1] == 1 and ";" in df.columns[0]:
        cols = [c.strip() for c in df.columns[0].split(";")]
        rows = []
        for raw in df.iloc[:, 0].astype(str):
            parts = [p.strip() for p in raw.split(";")]
            parts += [""] * (len(cols) - len(parts))
            rows.append(parts[:len(cols)])
        df = pd.DataFrame(rows, columns=cols)

    lower = {c.lower(): c for c in df.columns}
    def _find(*alts):
        for a in alts:
            if a in lower:
                return lower[a]
        return None

    c_periodo = _find("periodo", "trimestre", "tempo", "quarter")
    c_local   = _find("local", "uf", "regiao", "região", "territorio")
    c_grupo   = _find("grupo", "categoria", "tipo")
    c_media   = _find("media", "renda_media", "valor", "mean")

    missing = [n for n, c in [("trimestre/periodo", c_periodo), ("local", c_local),
                              ("grupo", c_grupo), ("media", c_media)] if c is None]
    if missing:
        raise RuntimeError(f"CSV sem colunas obrigatórias: {missing}. Colunas disponíveis: {list(df.columns)}")

    df = df.rename(columns={c_periodo:"periodo", c_local:"local", c_grupo:"grupo", c_media:"media"})
    df["periodo"] = _norm_periodo(df["periodo"])
    df["local"] = df["local"].astype(str)
    df["grupo"] = df["grupo"].astype(str)

    # vírgula decimal -> ponto; remove milhar
    df["media"] = (df["media"].astype(str)
                      .str.replace(".", "", regex=False)
                      .str.replace(",", ".", regex=False))
    df["media"] = pd.to_numeric(df["media"], errors="coerce")

    df = df.dropna(subset=["periodo", "local", "grupo", "media"])
    return df

def _pick_annual_row(g: pd.DataFrame, ano: int) -> pd.Series:
    """Escolhe T4 (<=2024) e T2 (2025) como observação anual."""
    cand = g[g["periodo"].str.startswith(str(ano))]
    if cand.empty:
        return pd.Series(dtype=float)
    ordem = {"T4":4, "T3":3, "T2":2, "T1":1}
    if ano <= 2024:
        cand = cand.assign(_k=cand["periodo"].str[-2:].map(ordem).fillna(0))
        return cand.sort_values("_k", ascending=False).iloc[0]
    t2 = cand[cand["periodo"].str.endswith("T2")]
    if not t2.empty:
        return t2.iloc[0]
    cand = cand.assign(_k=cand["periodo"].str[-2:].map(ordem).fillna(0))
    return cand.sort_values("_k", ascending=False).iloc[0]

def _to_uniform_series(df: pd.DataFrame) -> pd.DataFrame:
    """Tabela anual 2019..2025 por local, colunas: renda_formal, renda_informal (a partir de 'media')."""
    anos, labels = _build_year_axis()
    rows = []
    # pivot por (local, periodo) -> colunas de grupos
    piv = (df.pivot_table(index=["local", "periodo"], columns="grupo", values="media", aggfunc="mean")
             .reset_index())
    for loc, g in piv.groupby("local", sort=False):
        for i, ano in enumerate(anos):
            r = _pick_annual_row(g, ano)
            if r.empty:
                continue
            rows.append({
                "local": loc,
                "x_idx": i,
                "x_label": labels[i],
                "ano": ano,
                "renda_formal": float(r.get("Formais", np.nan)),
                "renda_informal": float(r.get("Informais", np.nan)),
            })
    out = pd.DataFrame(rows)
    return out[out["local"].isin(FOCO_LOCAIS)].copy()

def _fmt_rs(v: float) -> str:
    return f"R${v:,.0f}".replace(",", ".")

def _plot_series(ax, x, y, color, label):
    ax.plot(x[:-1], y[:-1], color=color, linewidth=2.6, marker="o", markersize=3.8,
            label=label, zorder=2)
    ax.plot(x[-2:], y[-2:], color=color, linewidth=2.6, linestyle="--",
            marker="o", markersize=3.8, zorder=2)

def _mark_last_point(ax, x_last, y_last, color):
    ax.scatter([x_last], [y_last], s=74, color=color, edgecolors="white", linewidths=1.1, zorder=4)
    ax.scatter([x_last], [y_last], s=100, facecolors="none", edgecolors=HIGHLIGHT_COLOR, linewidths=1.3, zorder=4)

def _label_points(ax, x, y, color, where: str, dy_px_below=16, dy_px_above=12):
    """
    Rótulos em TODOS os pontos.
    where: 'below' (abaixo) ou 'above' (acima).
    """
    for xi, yi in zip(x, y):
        if np.isnan(yi):
            continue
        if where == "above":
            ax.annotate(
                _fmt_rs(yi), xy=(xi, yi),
                xytext=(0, +dy_px_above), textcoords="offset points",
                ha="center", va="bottom", fontsize=9.0, color=color, weight="bold",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.55),
                clip_on=False, zorder=5
            )
        else:  # below
            ax.annotate(
                _fmt_rs(yi), xy=(xi, yi),
                xytext=(0, -dy_px_below), textcoords="offset points",
                ha="center", va="top", fontsize=9.0, color=color, weight="bold",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.55),
                clip_on=False, zorder=5
            )

# ----------------- principal -----------------
def main(path_csv: str = CSV_DEFAULT):
    # 1) leitura + sanidade
    df = _safe_read_csv(path_csv)
    df = df[df["local"].isin(FOCO_LOCAIS) & df["grupo"].isin(["Formais", "Informais"])].copy()
    assert_min_rows(df, MIN_ROWS, "renda média (deflacionada) — form/informais")

    # 2) anual uniforme 2019..2025 com pivot
    df_u = _to_uniform_series(df)

    # 3) estilo global
    plt.rcParams.update({
        "figure.figsize": (15.2, 7.0),
        "axes.facecolor": "white",
        "axes.grid": True, "grid.color": "#eaeaea", "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "savefig.bbox": "tight",
    })
    fig, axes = plt.subplots(1, 3, sharex=True, sharey=True)

    labels = [str(a)[-2:] for a in range(2019, 2026)]
    x_grid = np.arange(len(labels))

    expected_labels_per_panel = 0
    for ax, local in zip(axes, FOCO_LOCAIS):
        sub = df_u[df_u["local"] == local].sort_values("x_idx")
        x = sub["x_idx"].to_numpy(dtype=float)
        y_form = sub["renda_formal"].to_numpy(dtype=float)
        y_inf  = sub["renda_informal"].to_numpy(dtype=float)

        _plot_series(ax, x, y_form, PALETA_SERIES["Formais"], "Formais")
        _plot_series(ax, x, y_inf,  PALETA_SERIES["Informais"], "Informais")

        _mark_last_point(ax, x[-1], y_form[-1], PALETA_SERIES["Formais"])
        _mark_last_point(ax, x[-1], y_inf[-1],  PALETA_SERIES["Informais"])

        # Regras de colocação dos rótulos:
        # - Formais: sempre ABAIXO
        # - Informais: Nordeste e RN ACIMA; Brasil ABAIXO
        _label_points(ax, x, y_form, PALETA_SERIES["Formais"], where="below", dy_px_below=16)
        if local in ("Nordeste", "Rio Grande do Norte"):
            _label_points(ax, x, y_inf, PALETA_SERIES["Informais"], where="above", dy_px_above=12)
        else:
            _label_points(ax, x, y_inf, PALETA_SERIES["Informais"], where="below", dy_px_below=30)

        ax.set_title(local, fontsize=12, loc="left", pad=4,
                     bbox=dict(boxstyle="round,pad=0.25", fc="#f7f7f7", ec="#e0e0e0", lw=0.8))
        ax.set_xticks(x_grid)
        ax.set_xticklabels(labels)
        ax.set_xlim(x_grid.min()-0.15, x_grid.max()+0.15)
        ax.set_ylabel("Renda (R$)")

        if expected_labels_per_panel == 0:
            expected_labels_per_panel = int(np.sum(~np.isnan(y_form)) + np.sum(~np.isnan(y_inf)))

    # 5) limites Y e formatação — folgas superior e inferior para rótulos
    all_vals = pd.concat([df_u["renda_formal"], df_u["renda_informal"]]).astype(float).values
    y_min = max(0, int(math.floor(np.nanmin(all_vals) - 220)))
    y_max = int(math.ceil(np.nanmax(all_vals) + 220))
    for ax in axes:
        ax.set_ylim(y_min, y_max)
        ax.margins(y=0.12)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, pos=None: f"R${v:,.0f}".replace(",", ".")))

    # 6) legenda inferior
    leg = fig.legend(
        handles=[Line2D([0],[0], color=PALETA_SERIES["Formais"], lw=3),
                 Line2D([0],[0], color=PALETA_SERIES["Informais"], lw=3),
                 Line2D([0],[0], color=HIGHLIGHT_COLOR, lw=3, ls="--")],
        labels=["Formais", "Informais", "2025"],
        ncol=3, loc="lower center", bbox_to_anchor=(0.5, 0.04)
    )
    for h in getattr(leg, "legendHandles", []):
        if hasattr(h, "set_linewidth"): h.set_linewidth(3.0)

    plt.subplots_adjust(bottom=0.16, top=0.93, wspace=0.06)

    # ----------------- validações -----------------
    for i, ax in enumerate(axes, start=1):
        labels_here = [t.get_text() for t in ax.texts if isinstance(t.get_text(), str) and t.get_text().startswith("R$")]
        if len(labels_here) < expected_labels_per_panel:
            raise RuntimeError(
                f"Validação falhou no painel {i}: rótulos monetários insuficientes "
                f"({len(labels_here)} < {expected_labels_per_panel})."
            )
        if ax.get_xlabel():
            raise RuntimeError("Remova xlabel — o eixo X deve ter apenas os ticks de anos.")

    # ----------------- saída -----------------
    outdir = PROJECT_DIR / "outputs" / "figs"
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / "12_renda_formais_informais.png"
    plt.savefig(outfile, dpi=150)
    print(f"Figura salva em: {outfile}")

if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv) > 1 else CSV_DEFAULT
    main(csv)
