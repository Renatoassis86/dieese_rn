
# _scan_full.py
# Varredura completa da arquitetura do projeto
# Gera relatório em outputs/logs/scan_full.txt e imprime no terminal

from pathlib import Path
import datetime
import sys

ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "outputs" / "logs"
LOGS.mkdir(parents=True, exist_ok=True)
OUT = LOGS / "scan_full.txt"

# parâmetros
MAX_DEPTH = 6       # até quantos níveis descer
SHOW_HEAD = True    # se True, mostra amostras de CSV e scripts
HEAD_LINES = 5

def relpath(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)

def get_depth(p: Path) -> int:
    try:
        return len(p.relative_to(ROOT).parts)
    except Exception:
        return 0

def scan_tree():
    print("== VARREDURA COMPLETA ==")
    with OUT.open("w", encoding="utf-8") as f:
        header = f"# Varredura completa — {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n"
        f.write(header + "\n")
        print(header.strip())
        for p in sorted(ROOT.rglob("*")):
            depth = get_depth(p)
            if depth > MAX_DEPTH:
                continue
            size = p.stat().st_size if p.is_file() else ""
            mtime = datetime.datetime.fromtimestamp(p.stat().st_mtime)
            line = f"{'│   ' * (depth - 1)}{'├── ' if depth > 0 else ''}{p.name:<50}  {size:>10} bytes  {mtime:%Y-%m-%d %H:%M}"
            f.write(line + "\n")
            print(line)
        print(f"\nRelatório salvo em: {OUT}")

def sample_file(p: Path):
    """Retorna primeiras linhas do arquivo (CSV, PY, TXT, MD...)"""
    try:
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        head = lines[:HEAD_LINES]
        return "\n".join(head)
    except Exception as e:
        return f"[ERRO lendo {p.name}]: {e}"

def sample_data_files():
    """Amostra de conteúdo de CSVs e scripts"""
    with OUT.open("a", encoding="utf-8") as f:
        f.write("\n\n== AMOSTRAS DE ARQUIVOS ==\n")
        print("\n== AMOSTRAS DE ARQUIVOS ==")
        targets = list(ROOT.rglob("*.csv")) + list(ROOT.rglob("*.py")) + list(ROOT.rglob("*.xlsx"))
        for p in sorted(targets):
            if get_depth(p) > MAX_DEPTH:
                continue
            f.write(f"\n---- {relpath(p)} ----\n")
            print(f"\n---- {relpath(p)} ----")
            snippet = sample_file(p)
            f.write(snippet + "\n")
            print(snippet)
        print(f"\nAmostras registradas em {OUT}")

def main():
    scan_tree()
    if SHOW_HEAD:
        sample_data_files()
    print("\n✅ Varredura concluída com sucesso.")
    print(f"Arquivo de saída: {OUT}")

if __name__ == "__main__":
    main()
