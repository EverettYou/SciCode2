"""Synthesize completed artifacts and export a standalone scientific figure."""
from pathlib import Path
import json,os,tempfile
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'surface-qa-matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME',str(Path(tempfile.gettempdir())/'surface-qa-cache'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

LAB=Path(__file__).resolve().parents[1]


def best_mean(data,name,repaired=False):
    suffix='_repaired' if repaired else ''
    return [float(np.mean([max(c['scores'][i][name+suffix+'_one_run'],c['scores'][i][name+suffix+'_two_runs'])
        for c in data['cases']])) for i in range(len(data['aggregate']))]


def main():
    resources=json.loads((LAB/'results'/'resource_summary.json').read_text())
    native=json.loads((LAB/'results'/'dynamics_square2.json').read_text())
    physical=[]
    for seed in [11,29,47]:
        suffix='' if seed==11 else f'_seed{seed}'
        physical.append(json.loads((LAB/'results'/f'dynamics_physical_square2{suffix}.json').read_text()))
    rectangle=json.loads((LAB/'results'/'dynamics_rectangle23.json').read_text())
    assert all(d['status']=='complete' for d in [native,rectangle,*physical])
    times=[r['total_anneal_time'] for r in native['aggregate']]
    dual=[r['dual_two_sectors']['mean'] for r in native['aggregate']]
    raw_local=best_mean(native,'direct_local')
    repaired=best_mean(native,'direct_local',True)
    physical_local=np.array([best_mean(d,'direct_local',True) for d in physical])
    global_repaired=best_mean(native,'direct_global',True)
    summary={'resource_rows':resources['cases'],
        'dynamics_square2_rows':[dict(total_anneal_time=t,dual_two_sectors=d,
            direct_local_best_raw=a,direct_local_best_repaired=b,
            direct_global_best_repaired=c,physical_local_best_repaired_seed_range=[float(lo),float(hi)])
            for t,d,a,b,c,lo,hi in zip(times,dual,raw_local,repaired,global_repaired,
                                     physical_local.min(axis=0),physical_local.max(axis=0))],
        'rectangle23_rows':[dict(total_anneal_time=r['total_anneal_time'],
            dual_two_sectors=r['dual_two_sectors']['mean'],
            direct_local_best_repaired=v,direct_global_best_repaired=g) for r,v,g in
            zip(rectangle['aggregate'],best_mean(rectangle,'direct_local',True),best_mean(rectangle,'direct_global',True))],
        'validation':{'largest_steps_doubling_score_difference':max(d['max_refinement_score_difference'] for d in [native,rectangle,*physical]),
                      'largest_norm_error':max(d['max_norm_error'] for d in [native,rectangle,*physical])},
        'interpretation':'Direct best is the post-hoc better of one C run or two C/2 runs, chosen per instance; generous to direct, not a deployable oracle policy.'}
    (LAB/'results'/'comparison_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,(ax,bx)=plt.subplots(1,2,figsize=(12.5,4.7),constrained_layout=True)
    ds=[r['d'] for r in resources['cases']]
    qa=[r['direct']['physical_qubits_median'] for r in resources['cases']]
    qb=[r['dual']['physical_qubits_median'] for r in resources['cases']]
    ax.plot(ds,qa,'o-',color='#c45135',label='Error + XOR auxiliaries')
    ax.plot(ds,qb,'s-',color='#206f9b',label='Stabilizer, one sector at a time')
    ax.plot(ds,np.array(qb)*2,'s--',color='#7ba9c1',label='Two-sector nominal footprint*')
    ax.set_yscale('log');ax.set_xticks(ds)
    ax.set_xlabel('Surface-code distance d');ax.set_ylabel('Physical annealer qubits (median of 3 seeds)')
    ax.set_title('Same Zephyr Z6, same embedding search')
    ax.legend(loc='upper left',fontsize=8.5)
    ax.grid(alpha=.17)
    ax.text(.02,-.23,'*Doubled accounting only; simultaneous placement not constructed.',transform=ax.transAxes,fontsize=8)
    bx.plot(times,dual,'s-',color='#206f9b',label='Stabilizer: 2 sectors, C/2 each')
    bx.plot(times,repaired,'o-',color='#c45135',label='XOR + local penalty + repair (native)')
    bx.fill_between(times,physical_local.min(axis=0),physical_local.max(axis=0),color='#c45135',alpha=.13,
                    label='XOR: 3 physical embedding seeds')
    bx.plot(times,global_repaired,'^--',color='#777777',label='XOR + global penalty + repair (native)')
    bx.axhline(.3203125,color='#206f9b',linestyle=':',linewidth=1)
    bx.axhline(.310546875,color='#c45135',linestyle=':',linewidth=1)
    bx.set_xscale('log');bx.set_ylim(0,1.035)
    bx.set_xlabel('Total sequential anneal time C (dimensionless)')
    bx.set_ylabel('Mean probability of a minimum-weight correction')
    bx.set_title('Full forward anneal: 5-error-bit planar patch')
    bx.legend(loc='lower right',fontsize=8)
    bx.grid(alpha=.17)
    bx.text(.02,-.23,'All 4 syndromes × 2 weight sets; dotted: zero-time repaired baselines.',transform=bx.transAxes,fontsize=8)
    fig.savefig(LAB/'figures'/'encoding_comparison.png',dpi=190)
    fig.savefig(LAB/'figures'/'encoding_comparison.pdf')
    print(json.dumps(summary['dynamics_square2_rows'],indent=2))
    print(json.dumps(summary['rectangle23_rows'],indent=2))
    print(json.dumps(summary['validation']))

if __name__=='__main__':main()
