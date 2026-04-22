# src/plots_base.py
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ---------------- Paleta padrão ----------------
PALETA = {"Brasil": "#264653", "Nordeste": "#2A9D8F", "Rio Grande do Norte": "#E76F51"}
HIGHLIGHT_COLOR = "#6D597A"

# ---------------- Estilo global ----------------
def set_estilo_global():
    plt.rcParams.update({
        "font.size": 11,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "axes.edgecolor": "#444444",
        "axes.linewidth": 0.8,
        "xtick.color": "#333333",
        "ytick.color": "#333333",
        "figure.dpi": 120,
        "savefig.dpi": 300,
        "axes.grid": True,
        "grid.color": "#E6E6E6",
        "grid.linestyle": "-",
        "grid.linewidth": 0.8
    })

# ---------------- Estruturas ----------------
@dataclass
class Serie:
    nome: str                # "Brasil" | "Nordeste" | "Rio Grande do Norte"
    anos: List[int]          # [2019,...,2025]
    valores: List[float]     # valores em %

# ---------------- Utilitários de marcação ----------------
def _picos_e_vales(y: np.ndarray) -> Tuple[int, int]:
    return int(np.argmax(y)), int(np.argmin(y))

def _marcadores_especiais(ax, x, y, cor):
    """Marca primeiro, pico, vale e último ponto em todos os painéis."""
    idx_pico, idx_vale = _picos_e_vales(y)
    pontos = [0, idx_pico, idx_vale, len(x)-1]
    for i in sorted(set(pontos)):
        ax.scatter(x[i], y[i], s=30, color=cor, zorder=3, edgecolor="white", linewidth=0.8)

def _anel_no_ultimo(ax, xlast, ylast, cor):
    ax.scatter(xlast, ylast, s=120, facecolors="none", edgecolors=cor, linewidth=2.0, zorder=3)

def _linha_tracejada_2025(ax, x, y, cor):
    """Trecho tracejado 2024→2025 (realça o 2º tri de 2025)."""
    if 2024 in x and 2025 in x:
        i1, i2 = x.index(2024), x.index(2025)
        ax.plot([x[i1], x[i2]], [y[i1], y[i2]], linestyle="--", color=cor, linewidth=1.6, zorder=2)

def _rotulo_percentual(ax, x, y, texto, dx=0.08, dy=0.0):
    return ax.text(x+dx, y+dy, texto, ha="left", va="center", fontsize=10, color="#222222")

def _rotulo_ultimo_anticolisao(ax, xlast, ylast, texto):
    """Anti-colisão simples para o rótulo do último ponto no painel 1."""
    offsets = [0.0, 0.4, -0.4, 0.8]
    t = None
    for off in offsets:
        t = _rotulo_percentual(ax, xlast, ylast+off, texto)
        break
    return t

# ---------------- Box de variação ----------------
def _add_box_variacao(ax, d_br, d_ne, d_rn):
    box_text = (
        r"$\bf{Variação\ 19\rightarrow 25}$" + "\n"
        r"$\bf{BR}$   " + f"{d_br:+.1f} p.p.\n"
        r"$\bf{NE}$   " + f"{d_ne:+.1f} p.p.\n"
        r"$\bf{RN}$   " + f"{d_rn:+.1f} p.p."
    )
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.text(
        x0 + 0.98*(x1-x0), y0 + 0.98*(y1-y0),
        box_text, ha="right", va="top",
        fontsize=10, color="#222222",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#DDDDDD")
    )

# ---------------- Legenda padronizada ----------------
def _legend_quatro_colunas(fig, axes, paleta, highlight_color):
    handles = [
        Line2D([0], [0], color=paleta["Brasil"], linewidth=2.0, label="Brasil"),
        Line2D([0], [0], color=paleta["Nordeste"], linewidth=2.0, label="Nordeste"),
        Line2D([0], [0], color=paleta["Rio Grande do Norte"], linewidth=2.0, label="Rio Grande do Norte"),
        Line2D([0], [0], color=highlight_color, linestyle="--", linewidth=2.0, label="2025"),
    ]
    leg = fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, borderaxespad=0.0)
    for line in leg.get_lines():
        line.set_linewidth(2.0)

# ---------------- Eixos ----------------
def _config_eixo_x(ax, anos):
    ax.set_xticks(anos)
    ax.set_xticklabels([str(a)[-2:] for a in anos])  # 19…25
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    # Não setar xlabel -> garante ausência de "Anos"

def _config_eixo_y(ax):
    vals = ax.get_yticks()
    ax.set_yticklabels([f"{v:.0f}%" for v in vals])

# ---------------- Validações ----------------
def validar_rotulos_por_painel(axes):
    """Painel 1 com ≥1 textos contendo '%'; painéis 2 e 3 com 0 textos '%'. """
    def conta_textos_pct(ax):
        return sum(1 for t in ax.texts if '%' in (t.get_text() or ''))
    c0 = conta_textos_pct(axes[0])
    c1 = conta_textos_pct(axes[1]) if len(axes) > 1 else 0
    c2 = conta_textos_pct(axes[2]) if len(axes) > 2 else 0
    erros = []
    if c0 < 1:
        erros.append("Painel 1 deve conter ≥1 rótulo com '%'.")
    if c1 != 0:
        erros.append("Painel 2 não pode conter rótulos com '%'.")
    if c2 != 0:
        erros.append("Painel 3 não pode conter rótulos com '%'.")
    if erros:
        raise RuntimeError("Validação de rótulos por painel falhou: " + " ".join(erros))

def validar_marcadores_y_rotulos_y(axes, n_series_por_painel: int):
    """
    - Garante marcadores (scatter) em todos os painéis (>= n_series_por_painel).
    - Garante ylabel apenas no 1º painel; nos demais deve estar vazio.
    - Garante que nenhum painel possua xlabel (sem 'Anos').
    """
    erros = []
    for i, ax in enumerate(axes):
        # 1) Marcadores
        scatters = [c for c in ax.collections if c.__class__.__name__ == "PathCollection"]
        if len(scatters) < n_series_por_painel:  # há vários scatters por série; este é um piso conservador
            erros.append(f"Painel {i+1} sem marcadores suficientes.")

        # 2) Y label
        yl = ax.get_ylabel() or ""
        if i == 0 and yl.strip() == "":
            erros.append("Painel 1 deve exibir o ylabel 'Percentual (%)'.")
        if i > 0 and yl.strip() != "":
            erros.append(f"Painel {i+1} não deve exibir ylabel (deve ficar vazio).")

        # 3) X label (não pode haver 'Anos' ou qualquer xlabel)
        xl = ax.get_xlabel() or ""
        if xl.strip() != "":
            erros.append(f"Painel {i+1} não deve exibir xlabel (remova '{xl.strip()}').")

    if erros:
        raise RuntimeError("Validação de marcadores/rotulagem de eixos falhou: " + " ".join(erros))

# ---------------- Função principal (1–3 painéis) ----------------
def plot_linhas_paineis(
    series_por_painel: List[List[Serie]],
    nomes_paineis: List[str],
    paleta: Dict[str, str] = PALETA,
    highlight_color: str = HIGHLIGHT_COLOR,
    figsize=(12, 4.6),
    y_label="Percentual (%)"
):
    """
    Renderiza 1–3 painéis de linhas com padrão DT/ST e validações:
      - BR/NE/RN em cada painel;
      - marcadores (1º, pico, vale e último) em todos os painéis;
      - traço tracejado 2024→2025 e anel no último ponto;
      - rótulos (%) apenas no painel 1;
      - box de variação 19→25 em todos os painéis;
      - legenda inferior (4 colunas), incluindo '2025' tracejado;
      - validações automáticas ao final.
    """
    set_estilo_global()
    n = len(series_por_painel)
    fig, axes = plt.subplots(1, n, figsize=figsize, sharey=True)
    if n == 1:
        axes = [axes]

    anos_base = series_por_painel[0][0].anos
    for ax, series, titulo in zip(axes, series_por_painel, nomes_paineis):
        # Linhas + marcações
        for s in series:
            x = list(s.anos); y = list(s.valores)
            ax.plot(x, y, color=paleta[s.nome], linewidth=2.0, zorder=2)
            _marcadores_especiais(ax, x, np.array(y), paleta[s.nome])
            _linha_tracejada_2025(ax, x, y, paleta[s.nome])
            _anel_no_ultimo(ax, x[-1], y[-1], paleta[s.nome])

        # Rótulos apenas no 1º painel
        if ax is axes[0]:
            for s in series:
                x = list(s.anos); y = list(s.valores)
                _rotulo_ultimo_anticolisao(ax, x[-1], y[-1], f"{y[-1]:.1f}%")

        # Box 19→25
        def dif_19_25(s: Serie) -> float:
            i19 = s.anos.index(2019); i25 = s.anos.index(2025)
            return s.valores[i25] - s.valores[i19]
        d_br = dif_19_25(next(s for s in series if s.nome == "Brasil"))
        d_ne = dif_19_25(next(s for s in series if s.nome == "Nordeste"))
        d_rn = dif_19_25(next(s for s in series if s.nome == "Rio Grande do Norte"))
        _add_box_variacao(ax, d_br, d_ne, d_rn)

        # Eixos
        _config_eixo_x(ax, anos_base)
        _config_eixo_y(ax)
        ax.set_title(titulo, loc="left", pad=4)

    # Rótulos de eixos: Y só no 1º painel
    axes[0].set_ylabel(y_label)
    for ax in axes[1:]:
        ax.set_ylabel("")

    # Legenda inferior
    _legend_quatro_colunas(fig, axes, paleta, highlight_color=highlight_color)

    # Layout e VALIDAÇÕES
    fig.subplots_adjust(bottom=0.18, wspace=0.08)
    validar_rotulos_por_painel(axes)
    validar_marcadores_y_rotulos_y(axes, n_series_por_painel=len(series_por_painel[0]))

    return fig, axes
