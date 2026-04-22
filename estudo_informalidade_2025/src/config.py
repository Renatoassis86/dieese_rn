from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT_DIR / "outputs"
FIG_DIR = OUTPUT_DIR / "figs"
LOG_DIR = OUTPUT_DIR / "logs"
FIG_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

DATA_DIR_CANDIDATES = [
    PROJECT_DIR,
    PROJECT_DIR / "data",
    PROJECT_DIR.parent,
    Path(r"D:\repositorio_geral\pnad_continua"),
]
