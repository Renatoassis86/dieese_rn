import matplotlib.pyplot as plt

def add_explainer(ax: plt.Axes, xy: tuple[float,float], text: str, xytext=(10,10)) -> None:
    ax.annotate(text, xy=xy, xytext=xytext, textcoords="offset points",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#555"),
                ha="left", va="bottom", fontsize=9, color="#333")
