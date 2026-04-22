# file: scripts/22_renda_formal_informal_alt.py
import matplotlib.pyplot as plt
from pathlib import Path
from src.config import FIG_DIR
from src.style import apply_matplotlib_style
from src.io_utils import read_csv_safely, coerce_period_column
from src.plots import plot_evolution, EvolutionSpec
from src.schema import standardize_dataframe, guess_group_column, guess_metric_column

def main():
    path = Path("renda_formal_informal.csv")
    df = read_csv_safely(path)
    df = df.rename(columns={"trimestre":"periodo","ano":"periodo","situacao":"grupo","condicao":"grupo","tipo":"grupo",
                            "renda_media":"renda","media":"renda"})
    df = standardize_dataframe(df); df = coerce_period_column(df, "periodo")
    if "grupo" not in df.columns:
        cand = guess_group_column(df, {"periodo"})
        if cand: df = df.rename(columns={cand:"grupo"})
    y = "renda" if "renda" in df.columns else guess_metric_column(df, {"periodo","grupo"})
    if y != "renda" and y: df = df.rename(columns={y:"renda"})

    spec = EvolutionSpec(
        x_col="periodo", y_col="renda", group_col="grupo",
        y_label="Renda média (deflacionada)", x_label="Período",
        fname="22_renda_formal_informal_alt.png", show_trend=True, grey_all_first=True, add_title=False
    )
    fig = plot_evolution(df, spec); out = FIG_DIR / spec.fname
    apply_matplotlib_style(); plt.tight_layout(); fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig); print(out)

if __name__ == "__main__":
    main()
