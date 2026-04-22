from src.config import FIG_DIR
from src.io_utils import read_csv_safely
from src.schema import standardize_dataframe
from src.plots import plot_evolution, EvolutionSpec

def main():
    df = read_csv_safely("T2b_mix_setorial_informais.csv")
    df = standardize_dataframe(df)

    xcol = "periodo"
    gcol = "grupo" if "grupo" in df.columns else None  # deve virar o setor/cnae
    ycol = "part_informais" if "part_informais" in df.columns else "taxa_informalidade"  # fallback visual

    if ycol not in df.columns:
        raise ValueError(f"Não encontrei coluna de participação/taxa para o mix setorial. Colunas: {list(df.columns)}")

    spec = EvolutionSpec(x_col=xcol, y_col=ycol, group_col=gcol, fname="07_mix_setorial_informais.png", ylabel="Participação (%)")
    fig = plot_evolution(df, spec)
    out = FIG_DIR / spec.fname
    fig.savefig(out, dpi=300)
    print(f"Figura salva em: {out}")

if __name__ == "__main__":
    main()
