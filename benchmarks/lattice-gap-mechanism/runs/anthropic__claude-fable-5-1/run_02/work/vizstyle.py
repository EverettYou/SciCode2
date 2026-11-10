import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
C = {'half':'#2a78d6', '03':'#eb6834', '02':'#1baf7a', 'violet':'#6250d6', 'red':'#e34948',
     'ink':'#0b0b0b', 'ink2':'#52514e', 'muted':'#898781', 'grid':'#e1e0d9', 'axis':'#c3c2b7', 'surface':'#fcfcfb', 'page':'#f9f9f7'}
LABEL = {'half':r'$\nu=1/2$', '03':r'$\nu\approx0.3$', '02':r'$\nu\approx0.2$'}
SEQ = LinearSegmentedColormap.from_list('seqblue', ['#fcfcfb','#cde2fb','#9ec5f4','#6da7ec','#3987e5','#256abf','#184f95','#0d366b'])
DIV = LinearSegmentedColormap.from_list('divbr', ['#0d366b','#2a78d6','#9ec5f4','#f0efec','#f3a9a8','#e34948','#7a1c1c'])
def setup():
    plt.rcParams.update({'font.family':'sans-serif','font.size':10,'axes.edgecolor':C['axis'],'axes.labelcolor':C['ink2'],
        'xtick.color':C['ink2'],'ytick.color':C['ink2'],'axes.grid':True,'grid.color':C['grid'],'grid.linewidth':0.6,
        'axes.facecolor':C['surface'],'figure.facecolor':C['surface'],'savefig.facecolor':C['surface'],
        'legend.frameon':False,'axes.titlecolor':C['ink'],'lines.linewidth':2.0,'axes.spines.top':False,'axes.spines.right':False})
