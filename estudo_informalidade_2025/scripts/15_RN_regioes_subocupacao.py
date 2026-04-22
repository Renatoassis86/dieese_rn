# -*- coding: utf-8 -*-
# 15_subocupacao_regioes_RN.py
# Barras horizontais por REGIÃO (RN): grupo de ANOS (2019..2025) por linha
# Métrica: taxa de subocupação (%)

from pathlib import Path
import sys, re, unicodedata, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- bootstrap (src/*)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import PROJECT_DIR

CSV_DEFAULT = "data/T8a_RN_regioes_subocupacao.csv"

# Paletas de azuis por REGIÃO (cada uma com 7 tons — 2019..2025)
PALETAS_REGIAO = {
    "Oeste":   ["#C9D7E1","#B7CBD8","#A5C0D0","#93B4C7","#81A8BF","#6F9DB6","#5C91AE"],
    "Central": ["#C8D9EA","#B3CAE3","#9EBBDB","#89ACD4","#749DCD","#5F8EC5","#497FBE"],
    "Agreste": ["#CFE1F2","#B9D3ED","#A3C5E7","#8DB7E2","#77A9DC","#619BD7","#4B8DD1"],
    "Natal":   ["#CCDCE9","#B8CDDE","#A4BED3","#90AFC8","#7CA0BD","#6891B2","#5482A7"],
    "Entorno Metropolitano de Natal": ["#D4E5F3","#BFD6ED","#A9C8E8","#93BAE2","#7DACDD","#679ED7","#5191D2"],
}
# Mapeamentos de nomes existentes -> chaves acima
ALIAS = {
    "Oeste do RN": "Oeste",
    "Central do RN": "Central",
    "Agreste do RN": "Agreste",
    "Natal(RN)": "Natal",
    "Entorno metropolitano de Natal(RN)": "Entorno Metropolitano de Natal",
}

def _build_year_axis():
    anos = list(range(2019, 2025+1))
    labels = [str(a) for a in anos]
    return anos, labels

def _norm_periodo(s: pd.Series) -> pd.Series:
    def f(v):
        v0 = str(v)
        v1 = unicodedata.normalize("NFKD", v0).replace("Â","").replace("º","").replace("°","").replace(" ","")
        m = re.search(r"([1-4])tri[\/\-]?(20\d{2})", v1, flags=re.I)
        if m:  # 4tri/2019 -> 2019T4
            return f"{m.group(2)}T{m.group(1)}"
        m2 = re.search(r"(20\d{2})", v1)
        if m2:
            y = m2.group(1)
            return "2025T2" if y == "2025" else f"{y}T4"
        return v0
    return s.astype(str).map(f)

def _safe_read(path_csv: str) -> pd.DataFrame:
    def read_any(p):
        try:
            return pd.read_csv(p, sep=None, engine="python", dtype=str)
        except Exception:
            return pd.read_csv(p, sep=None, engine="python", dtype=str, encoding="latin-1")

    df = read_any(path_csv)
    # CSV colado com ';'
    if df.shape[1] == 1 and ";" in df.columns[0]:
        cols = [c.strip() for c in df.columns[0].split(";")]
        rows = []
        for raw in df.iloc[:,0].astype(str):
            parts = [p.strip() for p in raw.split(";")]
            rows.append(parts + [""]*(len(cols)-len(parts)))
        df = pd.DataFrame(rows, columns=cols)

    lower = {c.lower(): c for c in df.columns}
    def find(*alts):
        for a in alts:
            if a in lower:
                return lower[a]
        return None

    c_per = find("periodo","trimestre")
    c_reg = find("regiao","região","local")
    c_tax = find("tx_subocup","taxa","valor","tx")

    missing = [n for n,c in [("periodo",c_per),("regiao",c_reg),("taxa",c_tax)] if c is None]
    if missing:
        raise RuntimeError(f"CSV sem colunas obrigatórias: {missing}. Colunas disponíveis: {list(df.columns)}")

    df = df.rename(columns={c_per:"periodo", c_reg:"regiao", c_tax:"taxa"})
    df["periodo"] = _norm_periodo(df["periodo"])
    df["regiao"]  = df["regiao"].map(lambda x: ALIAS.get(str(x), str(x)))
    df["taxa"] = pd.to_numeric(df["taxa"].astype(str).str.replace(",",".",regex=False), errors="coerce")
    df = df.dropna(subset=["periodo","regiao","taxa"])
    return df

def _pick_ano(g: pd.DataFrame, ano: int) -> float:
    cand = g[g["periodo"].str.startswith(str(ano))]
    if cand.empty: 
        return np.nan
    if ano <= 2024:
        t4 = cand[cand["periodo"].str.endswith("T4")]
        row = t4.iloc[0] if not t4.empty else cand.iloc[-1]
    else:
        t2 = cand[cand["periodo"].str.endswith("T2")]
        row = t2.iloc[0] if not t2.empty else cand.iloc[-1]
    return float(row["taxa"])

def main(path_csv: str = CSV_DEFAULT):
    df = _safe_read(path_csv)

    # regiões na ordem desejada, caso existam
    regioes_ordem = [r for r in ["Oeste","Central","Agreste","Natal","Entorno Metropolitano de Natal"] if r in df["regiao"].unique()]
    if len(regioes_ordem) < 3:
        raise RuntimeError("Poucas regiões após leitura. Verifique a coluna 'regiao'.")

    anos, anos_lbl = _build_year_axis()
    y_base = np.arange(len(regioes_ordem))
    width = 0.11  # estreito para caber 7 barras por região

    plt.rcParams.update({
        "figure.figsize": (16, 7.8),
        "axes.facecolor": "white",
        "axes.grid": True, "grid.color": "#eaeaea", "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "savefig.bbox": "tight",
    })

    fig, ax = plt.subplots(1,1)

    # Deslocamentos verticais (centro de cada grupo)
    offsets = np.linspace(-width*3, width*3, len(anos))

    # Contagem de rótulos por região (para validar)
    rotulos_count = {r:0 for r in regioes_ordem}

    for i, reg in enumerate(regioes_ordem):
        base = df[df["regiao"] == reg]
        vals = []
        for ano in anos:
            vals.append(_pick_ano(base, ano))

        # barras ano a ano para a região i
        pals = PALETAS_REGIAO.get(reg, ["#BFD6ED","#A9C8E8","#93BAE2","#7DACDD","#679ED7","#5191D2","#3B83CC"])
        for j, (ano, v) in enumerate(zip(anos, vals)):
            if np.isnan(v): 
                continue
            y = y_base[i] + offsets[j]
            b = ax.barh(y, v, height=width*0.95, color=pals[j], edgecolor=pals[j], zorder=2)
            # rótulo à direita da barra
            ax.annotate(f"{v:.1f}%", xy=(v, y), xytext=(4,0), textcoords="offset points",
                        ha="left", va="center", fontsize=9, weight="bold",
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.6))
            rotulos_count[reg] += 1

    ax.set_yticks(y_base)
    ax.set_yticklabels(regioes_ordem, fontsize=11)
    ax.set_xlabel("Percentual (%)")
  

    # Limite X com folga
    xmax = math.ceil(np.nanmax(df["taxa"].values) + 3)
    ax.set_xlim(0, xmax)

    # legenda dos anos (amostra com tons da primeira região)
    sample = PALETAS_REGIAO[regioes_ordem[0]]
    handles = [plt.Line2D([0],[0], color=sample[k], lw=8) for k in range(len(anos))]
    fig.legend(handles, [str(a) for a in anos], ncol=7, loc="lower center", bbox_to_anchor=(0.5, 0.03))


    plt.subplots_adjust(bottom=0.14, top=0.90, left=0.20, right=0.96)

    # validação: todas as regiões com ≥1 rótulo
    if not all(v > 0 for v in rotulos_count.values()):
        raise RuntimeError(f"Validação falhou: há região sem rótulos. Contagens: {rotulos_count}")

    outdir = PROJECT_DIR / "outputs" / "figs"
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / "15_subocupacao_regioes_RN.png"
    fig.savefig(outfile, dpi=150)
    print(f"Figura salva em: {outfile}")

if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv) > 1 else CSV_DEFAULT
    main(csv)
print(">>> EXECUTANDO:", __file__)
print(">>> LEGENDA ANOS:", [str(a) for a in range(2019, 2026)])
print(">>> SAÍDA:", (PROJECT_DIR / "outputs" / "figs" / "15_subocupacao_regioes_RN.png"))
