# -*- coding: utf-8 -*-
# 17_previdencia_regioes_RN.py
# Barras VERTICAIS por REGIÃO (RN): ANOS (2019..2025)
# Métrica: % que contribui para previdência ENTRE OS OCUPADOS INFORMAIS

from pathlib import Path
import sys, re, unicodedata, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- bootstrap projeto ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import PROJECT_DIR

CSV_DEFAULT = "data/T8c_RN_regioes_previdencia.csv"

# Paletas por região (7 tons de azul — 2019..2025)
PALETAS_REGIAO = {
    "Oeste":   ["#C9D7E1","#B7CBD8","#A5C0D0","#93B4C7","#81A8BF","#6F9DB6","#5C91AE"],
    "Central": ["#C8D9EA","#B3CAE3","#9EBBDB","#89ACD4","#749DCD","#5F8EC5","#497FBE"],
    "Agreste": ["#CFE1F2","#B9D3ED","#A3C5E7","#8DB7E2","#77A9DC","#619BD7","#4B8DD1"],
    "Natal":   ["#CCDCE9","#B8CDDE","#A4BED3","#90AFC8","#7CA0BD","#6891B2","#5482A7"],
    "Entorno Metropolitano de Natal": ["#D4E5F3","#BFD6ED","#A9C8E8","#93BAE2","#7DACDD","#679ED7","#5191D2"],
}

ALIAS = {
    "Oeste do RN":"Oeste","Central do RN":"Central","Agreste do RN":"Agreste",
    "Natal(RN)":"Natal","Entorno metropolitano de Natal(RN)":"Entorno Metropolitano de Natal",
}

def _anos():
    anos = list(range(2019, 2025+1))
    return anos, [str(a) for a in anos]

def _norm_periodo(s: pd.Series) -> pd.Series:
    def f(v):
        v0 = str(v)
        v1 = unicodedata.normalize("NFKD", v0).replace("º","").replace("°","").replace(" ","")
        m = re.search(r"([1-4])tri[\/\-]?(20\d{2})", v1, flags=re.I)
        if m: 
            return f"{m.group(2)}T{m.group(1)}"
        m2 = re.search(r"(20\d{2})", v1)
        if m2:
            y = m2.group(1)
            return "2025T2" if y=="2025" else f"{y}T4"
        return v0
    return s.astype(str).map(f)

def _read_previd(path_csv: str) -> pd.DataFrame:
    def read_any(p):
        try:
            return pd.read_csv(p, sep=None, engine="python", dtype=str)
        except Exception:
            return pd.read_csv(p, sep=None, engine="python", dtype=str, encoding="latin-1")

    df = read_any(path_csv)

    # CSV colado com ';'
    if df.shape[1]==1 and ";" in df.columns[0]:
        cols=[c.strip() for c in df.columns[0].split(";")]
        rows=[]
        for raw in df.iloc[:,0].astype(str):
            parts=[p.strip() for p in raw.split(";")]
            rows.append(parts+[""]*(len(cols)-len(parts)))
        df=pd.DataFrame(rows, columns=cols)

    lower={c.lower():c for c in df.columns}

    def find(*alts):
        for a in alts:
            if a in lower: 
                return lower[a]
        return None

    c_tri=find("trimestre","periodo")
    c_loc=find("local","regiao","região")
    c_grp=find("grupo")
    c_pct=find("pct_contrib","pct","percentual","taxa","valor")

    df=df.rename(columns={c_tri:"periodo", c_loc:"regiao", c_grp:"grupo", c_pct:"pct"})
    df["periodo"]=_norm_periodo(df["periodo"])
    df["regiao"]=df["regiao"].map(lambda x: ALIAS.get(str(x), str(x)))
    df["pct"]=pd.to_numeric(df["pct"].astype(str).str.replace(",",".",regex=False), errors="coerce")

    # Apenas ocupados informais
    df=df[df["grupo"].str.contains("Informais", na=False)]
    df=df.dropna(subset=["periodo","regiao","pct"])

    return df

def _pick_year(g, ano):
    cand=g[g["periodo"].str.startswith(str(ano))]
    if cand.empty: 
        return np.nan
    if ano<=2024:
        t4=cand[cand["periodo"].str.endswith("T4")]
        row=t4.iloc[0] if not t4.empty else cand.iloc[-1]
    else:
        t2=cand[cand["periodo"].str.endswith("T2")]
        row=t2.iloc[0] if not t2.empty else cand.iloc[-1]
    return float(row["pct"])

def main(path_csv: str = CSV_DEFAULT):
    df=_read_previd(path_csv)

    regioes=[r for r in ["Oeste","Central","Agreste","Natal","Entorno Metropolitano de Natal"]
             if r in df["regiao"].unique()]

    anos, anos_lbl = _anos()

    # Config do gráfico vertical
    plt.rcParams.update({
        "figure.figsize": (16, 6),
        "axes.facecolor":"white",
        "axes.grid":True,
        "grid.color":"#eaeaea",
        "grid.linewidth":0.8,
        "axes.spines.top":False,
        "axes.spines.right":False,
        "legend.frameon":False,
        "savefig.bbox":"tight",
    })

    fig, ax = plt.subplots(1,1)

    x = np.arange(len(regioes))
    width = 0.10
    offsets = np.linspace(-width*3, width*3, len(anos))

    lblcount={r:0 for r in regioes}

    for j, ano in enumerate(anos):
        for i, reg in enumerate(regioes):
            g=df[df["regiao"]==reg]
            v=_pick_year(g, ano)
            if np.isnan(v): 
                continue

            xplot = x[i] + offsets[j]
            color = PALETAS_REGIAO[reg][j]

            ax.bar(xplot, v, width=width*0.95, color=color, edgecolor=color)

            # rótulo EM PÉ para não sobrepor outras barras
            ax.annotate(
                f"{v:.1f}%",
                xy=(xplot, v),
                xytext=(0, 2),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                weight="bold",
                rotation=90,  # <<< rótulo em pé
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.6)
            )
            lblcount[reg] += 1

    ax.set_xticks(x)
    ax.set_xticklabels(regioes, fontsize=11)
    ax.set_ylabel("Percentual (%)")
    

    # Limite Y ajustado ao dado (sem forçar 0–100)
    ymax = math.ceil(np.nanmax(df["pct"]) + 3)
    ax.set_ylim(0, ymax)

    # legenda com anos
    sample = PALETAS_REGIAO[regioes[0]]
    handles = [plt.Line2D([0],[0], color=sample[k], lw=8) for k in range(len(anos))]
    fig.legend(handles, anos_lbl, ncol=7, loc="lower center", bbox_to_anchor=(0.5, -0.08))

    if not all(v>0 for v in lblcount.values()):
        raise RuntimeError(f"Alguma região ficou sem rótulos: {lblcount}")

    outdir = PROJECT_DIR / "outputs" / "figs"
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / "17_previdencia_regioes_RN.png"
    fig.savefig(outfile, dpi=150)
    print(f"Figura salva em: {outfile}")

if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv)>1 else CSV_DEFAULT
    main(csv)
