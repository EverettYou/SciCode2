"""Empirical NMR/transport scales; no microscopic interpretation imposed.

Run with system Python 3.13 (numpy/scipy/matplotlib). Input stays unmodified.
Quoted sigmas are used as supplied; uncertainty estimates are NOT reduced when
reduced chi squared is below one. Normalization covariance was not supplied.
"""
from pathlib import Path
import json, os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/layered-oxide-mpl")
import numpy as np
from scipy.optimize import least_squares
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullFormatter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path((Path(__file__).resolve().parents[1] / 'data' / 'measurements.json'))
DATA = json.loads(SOURCE.read_text())
NMR, RHO = DATA["measurements"][1:]
RNG = np.random.default_rng(20261028)
COLORS = ["#B83046", "#16876B", "#326CC3"]
LABELS = [r"$\nu=1/2$", r"$\nu\simeq0.3$", r"$\nu\simeq0.2$"]
plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":10,
                    "axes.spines.top":False, "axes.spines.right":False,
                    "axes.labelsize":11, "legend.fontsize":9,
                    "savefig.dpi":220, "figure.dpi":120})


def arr(sample, key):
    return np.asarray(sample[key], float)


def model(theta, t, sign, power):
    q = theta[2] if power is None else power
    return np.exp(np.clip(theta[0] + q*np.log(t) + sign*theta[1]/t, -700, 700))


def fit_activation(t, y, sigma, sign, power, initial, nboot=0):
    def solve(yy, start):
        return least_squares(lambda v:(model(v,t,sign,power)-yy)/sigma,
                             start, max_nfev=500,
                             bounds=([-30,-20,-15] if power is None else [-30,-20],
                                     [30,30,15] if power is None else [30,30]))
    fit=solve(y, initial)
    cov=np.linalg.inv(fit.jac.T@fit.jac)
    chi=float(np.sum(fit.fun**2)); dof=len(t)-len(fit.x)
    out={"log_A":float(fit.x[0]), "A":float(np.exp(fit.x[0])),
         "activation_D":float(fit.x[1]),
         "activation_se_D":float(np.sqrt(cov[1,1])),
         "power_q":float(fit.x[2] if power is None else power),
         "power_fixed":power is not None, "covariance":cov.tolist(),
         "chi_square":chi, "degrees_of_freedom":dof,
         "reduced_chi_square":chi/dof, "n":len(t),
         "temperature_range_D":[float(t.min()),float(t.max())],
         "theta":fit.x.tolist(), "sign":sign,
         "AIC":chi+2*len(fit.x)}
    if power is None:out["power_q_se"]=float(np.sqrt(cov[2,2]))
    if nboot:
        mu=model(fit.x,t,sign,power)
        sims=np.array([solve(mu+RNG.normal(0,sigma),fit.x).x for _ in range(nboot)])
        out["parametric_bootstrap_replicates"]=nboot
        out["activation_bootstrap_68_D"]=np.percentile(sims[:,1],[16,84]).tolist()
        out["activation_bootstrap_95_D"]=np.percentile(sims[:,1],[2.5,97.5]).tolist()
        out["A_bootstrap_95"]=np.percentile(np.exp(sims[:,0]),[2.5,97.5]).tolist()
        if power is None:out["q_bootstrap_95"]=np.percentile(sims[:,2],[2.5,97.5]).tolist()
    return out


def linear_fit(t,y,sigma):
    x=np.column_stack([np.ones(len(t)),t]);w=x/sigma[:,None]
    cov=np.linalg.inv(w.T@w);beta=cov@w.T@(y/sigma)
    residual=(x@beta-y)/sigma
    return {"intercept":float(beta[0]),"slope_per_D":float(beta[1]),
            "standard_errors":np.sqrt(np.diag(cov)).tolist(),
            "covariance":cov.tolist(),"chi_square":float(residual@residual),
            "degrees_of_freedom":len(t)-2,
            "temperature_range_D":[float(t.min()),float(t.max())]}


def main():
    result={"source":str(SOURCE), "units":"D=1; k_B=1", "method":
            "Weighted Gaussian least squares in the supplied observable (1/T1 or rho), not logarithms. Independent quoted sigmas; no rescaling by reduced chi square. Parametric bootstrap, fixed supplied sigmas, seed 20261028.",
            "limitations":["No covariance of normalization errors is supplied; fits are conditional on independent quoted errors.",
                           "NMR activation is not automatically a microscopic singlet-triplet gap.",
                           "Transport activation is not automatically the STS gap or half of it.",
                           "Temperature exponents and fit windows cause model-dependent shifts.",
                           "Zero-resistivity samples carry zero quoted error; they define transition intervals and are excluded from positive-branch least squares."],
            "nmr":[],"resistivity":[]}
    for j,s in enumerate(NMR["samples"]):
        t,y,e=arr(s,"temperature"),arr(s,"one_over_T1"),arr(s,"uncertainty")
        hi=[5,5,.5][j];mask=t<=hi
        fixed=fit_activation(t[mask],y[mask],e[mask],-1,1,[1,[5.5,2.6,1.7][j]],2000)
        free=fit_activation(t[mask],y[mask],e[mask],-1,None,fixed["theta"]+[1],1000)
        windows=[]
        for cut in ([1,2,5] if j==0 else [.5,1,2,5,11]):
            m=t<=cut
            if m.sum()>=5:
                f=fit_activation(t[m],y[m],e[m],-1,1,fixed["theta"])
                windows.append(f)
        entry={"filling":s["filling"],"fixed_prefactor_fit":fixed,
               "free_prefactor_fit":free,"window_sensitivity":windows}
        if j==2:
            def weighted_mean(lo,hi):
                m=(t>=lo)&(t<=hi);v=y[m]/t[m];sig=e[m]/t[m]
                se=np.sum(1/sig**2)**-.5;av=np.sum(v/sig**2)*se**2
                return {"mean":float(av),"se":float(se),"n":int(m.sum()),"T_range_D":[lo,hi]}
            normal=weighted_mean(1.1712,10);enh=weighted_mean(.7372,1.0209)
            entry["normal_plateau_R_over_T"]=normal
            entry["below_transition_enhancement_R_over_T"]=enh
            entry["enhancement_contrast_sigma"]=(enh["mean"]-normal["mean"])/np.hypot(enh["se"],normal["se"])
            entry["enhancement_interpretation"]="Suggestive coherence-like enhancement (about 2.75 sigma under independent errors), not proof of pairing symmetry."
        result["nmr"].append(entry)
    for j,s in enumerate(RHO["samples"]):
        t,y,e=arr(s,"temperature"),arr(s,"resistivity"),arr(s,"uncertainty")
        mask=(y>0)&(e>0);entry={"filling":s["filling"]}
        if j<2:
            fixed=fit_activation(t[mask],y[mask],e[mask],1,0,[-1,[3.7,.9][j]],2000)
            free=fit_activation(t[mask],y[mask],e[mask],1,None,fixed["theta"]+[0],1000)
            entry.update(fixed_prefactor_fit=fixed,free_prefactor_fit=free)
            entry["window_sensitivity"]=[]
            for cut in [1,2,4]:
                m=mask&(t<=cut)
                entry["window_sensitivity"].append(fit_activation(t[m],y[m],e[m],1,0,fixed["theta"]))
        else:entry["linear_positive_branch_fit"]=linear_fit(t[mask],y[mask],e[mask])
        if np.any(y==0):
            last_zero=float(t[y==0].max());first_positive=float(t[(t>last_zero)&(y>0)].min())
            entry["transition_interval_D"]=[last_zero,first_positive]
            entry["transition_interval_convention"]="last zero < Tc <= first positive (if zero below and positive above Tc)"
        result["resistivity"].append(entry)
    path=ROOT/"data/nmr_transport_results.json"
    path.write_text(json.dumps(result,indent=2))
    make_plots(result)
    print(json.dumps({"result":str(path),"nmr_E":[x["fixed_prefactor_fit"]["activation_D"] for x in result["nmr"]],
                     "rho_E":[x["fixed_prefactor_fit"]["activation_D"] for x in result["resistivity"][:2]]},indent=2))


def make_plots(result):
    fig,axes=plt.subplots(2,3,figsize=(12,6.7),gridspec_kw={"height_ratios":[2.2,1]},layout="constrained")
    for j,s in enumerate(NMR["samples"]):
        t,y,e=arr(s,"temperature"),arr(s,"one_over_T1"),arr(s,"uncertainty")
        r=result["nmr"][j]["fixed_prefactor_fit"];v=np.array(r["theta"]);c=COLORS[j]
        ax,res=axes[:,j];x=1/t
        ax.errorbar(x,y/t,yerr=e/t,fmt="o",ms=3.5,color=c,ecolor=c,elinewidth=.7,capsize=1.5,label="Measurements")
        lo,hi=r["temperature_range_D"];tf=np.geomspace(lo,hi,400)
        pred=model(v,tf,-1,1)/tf
        ax.plot(1/tf,pred,color=c,lw=1.8,label="Activated fit")
        # Delta-method band using unscaled covariance, conditional on fixed power.
        cov=np.asarray(r["covariance"]);jac=np.column_stack([np.ones(len(tf)),-1/tf])
        sig=np.sqrt(np.einsum("ij,jk,ik->i",jac,cov,jac))
        ax.fill_between(1/tf,pred*np.exp(-sig),pred*np.exp(sig),color=c,alpha=.15,lw=0,label=r"Fit $1\sigma$")
        mask=(t>=lo)&(t<=hi);res.axhline(0,color=".4",lw=.7)
        res.axhspan(-1,1,color=c,alpha=.08,lw=0)
        res.plot(x[mask],(y[mask]-model(v,t[mask],-1,1))/e[mask],"o",ms=3.5,color=c)
        res.set(xlabel=r"$D/T$",ylim=(-3,3),xlim=(0,5.15))
        ax.set(yscale="log",xlim=(0,5.15),ylim=(8e-6,7),title=LABELS[j])
        ax.text(.04,.05,r"$E_s/D=%.3f\pm%.3f$"%(r["activation_D"],r["activation_se_D"]),transform=ax.transAxes,fontsize=10)
        if j==2:
            nr=result["nmr"][j]["normal_plateau_R_over_T"]
            ax.plot([0,1/1.1712],[nr["mean"]]*2,color=".3",ls="--",lw=1,label="Normal-state plateau")
            ax.axvspan(1/1.15,1/1.075,color=".6",alpha=.15,lw=0)
        if j==0:
            ax.set_ylabel(r"$[1/(T_1T)]/[1/(T_1T)]_{T=4D}$")
            res.set_ylabel("Residual / quoted error")
        ax.grid(axis="y",which="major",alpha=.15)
    axes[0,0].legend(loc="upper right",frameon=False,fontsize=8)
    axes[0,2].legend(loc="upper right",frameon=False,fontsize=8)
    fig.suptitle("NMR: activated response and a low-filling coherence-like enhancement",fontsize=14)
    fig.savefig(ROOT/"figures/nmr_transport_nmr.png",bbox_inches="tight")
    plt.close(fig)

    fig,axes=plt.subplots(2,3,figsize=(12,6.7),gridspec_kw={"height_ratios":[2.2,1]},layout="constrained")
    for j,s in enumerate(RHO["samples"]):
        t,y,e=arr(s,"temperature"),arr(s,"resistivity"),arr(s,"uncertainty")
        ax,res=axes[:,j];c=COLORS[j];entry=result["resistivity"][j];mask=e>0
        ax.errorbar(t,y,yerr=e,fmt="o",ms=3,color=c,ecolor=c,elinewidth=.7,capsize=1.5)
        tf=np.linspace(t[mask].min(),4,400)
        if j<2:
            r=entry["fixed_prefactor_fit"];v=np.array(r["theta"])
            pred=model(v,tf,1,0);fitted=model(v,t[mask],1,0)
            cov=np.array(r["covariance"]);jac=np.column_stack([np.ones(len(tf)),1/tf])
            sig=np.sqrt(np.einsum("ij,jk,ik->i",jac,cov,jac))
            low,high=pred*np.exp(-sig),pred*np.exp(sig)
            annotation=r"$E_\rho/D=%.3f\pm%.3f$"%(r["activation_D"],r["activation_se_D"])
        else:
            r=entry["linear_positive_branch_fit"];v=np.array([r["intercept"],r["slope_per_D"]])
            pred=v[0]+v[1]*tf;fitted=v[0]+v[1]*t[mask]
            cov=np.array(r["covariance"]);jac=np.column_stack([np.ones(len(tf)),tf])
            sig=np.sqrt(np.einsum("ij,jk,ik->i",jac,cov,jac));low,high=pred-sig,pred+sig
            annotation=r"$\rho/\rho(4D)=%.3f+%.3f(T/D)$"%tuple(v)
        ax.plot(tf,pred,color=c,lw=1.8,label="Positive-branch fit")
        ax.fill_between(tf,low,high,color=c,alpha=.15,lw=0,label=r"Fit $1\sigma$")
        if "transition_interval_D" in entry:
            a,b=entry["transition_interval_D"]
            ax.axvspan(a,b,color=".5",alpha=.18,lw=0,label=r"$T_c$ bracket")
            ax.plot([.1,a],[0,0],color=c,lw=1.8)
        ax.text(.04,.95,annotation,transform=ax.transAxes,va="top",fontsize=9)
        ax.set(title=LABELS[j],xlim=(0,4.1))
        if j==0:ax.set(yscale="log",ylim=(.7,3000))
        elif j==1:
            ax.set_yscale("symlog",linthresh=.2)
            ax.set(ylim=(-.02,14))
        else:ax.set(ylim=(-.03,1.2))
        ax.grid(axis="y",which="major",alpha=.15)
        res.axhline(0,color=".4",lw=.7);res.axhspan(-1,1,color=c,alpha=.08,lw=0)
        res.plot(t[mask],(y[mask]-fitted)/e[mask],"o",ms=3.3,color=c)
        res.set(xlabel=r"$T/D$",xlim=(0,4.1),ylim=(-3,3))
        if j==0:ax.set_ylabel(r"$\rho(T)/\rho(4D)$");res.set_ylabel("Residual / quoted error")
    axes[0,1].legend(loc="upper right",bbox_to_anchor=(1,.84),frameon=False,fontsize=8)
    fig.suptitle("Resistivity: insulating half filling, activated and metallic normal states",fontsize=14)
    fig.savefig(ROOT/"figures/nmr_transport_resistivity.png",bbox_inches="tight")
    plt.close(fig)

    # Compact model comparison, showing conditional statistical versus prefactor uncertainty.
    fig,axs=plt.subplots(1,2,figsize=(9.3,3.8),layout="constrained")
    for ax,series,title in zip(axs,[result["nmr"],result["resistivity"][:2]],
                               ["NMR activation", "Transport activation"]):
        for j,entry in enumerate(series):
            fixed,free=entry["fixed_prefactor_fit"],entry["free_prefactor_fit"]
            ax.errorbar(j-.08,fixed["activation_D"],yerr=fixed["activation_se_D"],fmt="o",color=COLORS[j],capsize=4,label="Fixed prefactor" if j==0 else None)
            ax.errorbar(j+.08,free["activation_D"],yerr=free["activation_se_D"],fmt="s",mfc="white",color=COLORS[j],capsize=4,label="Free temperature power" if j==0 else None)
        ax.set(xticks=range(len(series)),xticklabels=LABELS[:len(series)],ylabel=r"Activation energy / $D$",title=title)
        ax.grid(axis="y",alpha=.2)
    axs[0].legend(frameon=False,fontsize=9)
    fig.suptitle("Uncertainty depends on the prefactor model",fontsize=13)
    fig.savefig(ROOT/"figures/nmr_transport_uncertainty.png",bbox_inches="tight")
    plt.close(fig)


if __name__=="__main__":main()
