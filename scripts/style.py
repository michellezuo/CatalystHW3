"""Shared plot styling and small helpers for every figure in the project."""
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

# Categorical slots, fixed order (blue, orange, aqua, yellow, magenta, green, violet, red)
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]

BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
ORANGE_RAMP = ["#fde3d6", "#f9c0a5", "#f39a73", "#eb6834", "#c9501f", "#9c3b14", "#6e290d"]
SEQ_BLUE = LinearSegmentedColormap.from_list("seq_blue", BLUE_RAMP)
SEQ_ORANGE = LinearSegmentedColormap.from_list("seq_orange", ORANGE_RAMP)

# LISA cluster colors: diverging blue <-> red, gray for not significant
LISA_COLORS = {
    "High-High": "#d03b3b",
    "Low-Low": "#256abf",
    "High-Low": "#f2a7a3",
    "Low-High": "#9ec5f4",
    "Not significant": "#e9e8e3",
}


def apply():
    mpl.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": ["Segoe UI", "DejaVu Sans", "sans-serif"],
        "font.size": 11,
        "axes.edgecolor": AXIS,
        "axes.labelcolor": INK2,
        "axes.titlecolor": INK,
        "axes.titlesize": 14,
        "axes.titleweight": "semibold",
        "axes.titlelocation": "left",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.axisbelow": True,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": INK2,
        "ytick.labelcolor": INK2,
        "legend.frameon": False,
        "legend.labelcolor": INK2,
    })


def source_note(fig, text, y=0.01):
    fig.text(0.01, y, text, ha="left", va="bottom", fontsize=8.5, color=MUTED)


def save(fig, path):
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("saved", path)
