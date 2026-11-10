import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
INK='#0b0b0b'; INK2='#52514e'; MUTED='#898781'; GRID='#e1e0d9'; AXIS='#c3c2b7'; SURF='#fcfcfb'
S1,S2,S3='#2a78d6','#eb6834','#1baf7a'          # categorical slots 1-3 (validated all-pairs)
CRYSTAL={'1/2':S1,'≈0.3':S2,'≈0.2':S3}
MARK={'1/2':'o','≈0.3':'s','≈0.2':'^'}
BLUES=['#fcfcfb','#cde2fb','#9ec5f4','#6da7ec','#3987e5','#256abf','#184f95','#0d366b']
SEQ=LinearSegmentedColormap.from_list('seqblue',BLUES)
DIV=LinearSegmentedColormap.from_list('divbr',['#104281','#3987e5','#9ec5f4','#f0efec','#f2a8a8','#e34948','#9b1c1c'])
def setup():
    plt.rcParams.update({'font.family':'sans-serif','font.size':10,'axes.edgecolor':AXIS,'axes.labelcolor':INK,
        'xtick.color':INK2,'ytick.color':INK2,'axes.grid':True,'grid.color':GRID,'grid.linewidth':0.6,'grid.linestyle':'-',
        'axes.facecolor':SURF,'figure.facecolor':'white','legend.frameon':False,'lines.linewidth':2.0,
        'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':160})
