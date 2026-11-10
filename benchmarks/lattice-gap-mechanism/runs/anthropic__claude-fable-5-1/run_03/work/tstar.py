import json,numpy as np
d=json.load(open('/app/measurements.json'))
s=d['measurements'][1]['samples'][1]; T=np.array(s['temperature']); r=np.array(s['one_over_T1'])/T; u=np.array(s['uncertainty'])/T
print("nu=0.3 NMR 1/T1T for T>0.9:")
for t_,x,e in zip(T,r,u):
    if t_>0.9: print(f"  T={t_:5.2f}  1/T1T={x:.3f} +- {e:.3f}")
# a T-independent gap Delta with step-edge DOS: 1/T1T ~ exp(-Delta/T) normalized at T=4 where gap closed?; compute implied suppression factor data/metal
print("implied suppression ratio vs a Korringa value of 1.05:")
for t_,x in zip(T,r):
    if 0.9<t_<4.5: print(f"  T={t_:5.2f} ratio={x/1.05:.3f}  exp(-2.45/T)={np.exp(-2.45/t_):.3f}  ratio/exp={x/1.05/np.exp(-2.45/t_):.2f}")
