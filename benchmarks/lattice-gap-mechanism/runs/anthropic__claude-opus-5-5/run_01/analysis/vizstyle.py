"""Shared figure style (validated categorical slots, one-hue sequential ramp, blue<->red diverging)."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

SURFACE = '#fcfcfb'
INK = '#0b0b0b'
INK2 = '#52514e'
MUTED = '#898781'
GRID = '#e1e0d9'
AXIS = '#c3c2b7'

# categorical slots 1-3 (validated all-pairs, light mode); fixed entity assignment
C_HALF = '#2a78d6'   # nu = 1/2      (slot 1, blue)
C_03 = '#eb6834'     # nu ~ 0.3      (slot 2, orange)
C_02 = '#1baf7a'     # nu ~ 0.2      (slot 3, aqua)  -> always direct-labelled (contrast relief)
CRYSTAL = {'1/2': C_HALF, '0.3': C_03, '0.2': C_02}
MARK = {'1/2': 'o', '0.3': 's', '0.2': '^'}

BLUE_RAMP = ['#fcfcfb', '#cde2fb', '#b7d3f6', '#9ec5f4', '#86b6ef', '#6da7ec', '#5598e7', '#3987e5',
             '#2a78d6', '#256abf', '#1c5cab', '#184f95', '#104281', '#0d366b']
SEQ = LinearSegmentedColormap.from_list('seq_blue', BLUE_RAMP)
DIV = LinearSegmentedColormap.from_list('div_br', ['#184f95', '#3987e5', '#9ec5f4', '#f0efec',
                                                    '#f2a9a8', '#e66767', '#b52b2b'])


def apply():
    plt.rcParams.update({
        'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
        'axes.edgecolor': AXIS, 'axes.labelcolor': INK, 'xtick.color': INK2, 'ytick.color': INK2,
        'text.color': INK, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6,
        'grid.linestyle': '-', 'axes.linewidth': 0.8, 'lines.linewidth': 2.0, 'font.size': 10,
        'axes.titlesize': 11, 'legend.frameon': False, 'font.family': 'DejaVu Sans',
        'axes.spines.top': False, 'axes.spines.right': False,
    })
