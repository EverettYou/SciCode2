"""Cross-check C++ classical sampler against exact finite-step two-site evolution."""
from pathlib import Path
import numpy as np,json,csv,subprocess,time,math
OUT=Path(__file__).resolve().parents[1]/'results';SCRIPT=Path(__file__).resolve().parent

def main():
    start=time.perf_counter();config=OUT/'backend_check_input.txt';csvpath=OUT/'backend_check_output.csv'
    config.write_text('2 1 1 1 1 50000 1 5 173 1 0\n0.4 0\n0 1 -0.6\n0\n1 0 0\n1\n0 1\n20\n')
    subprocess.run([str(SCRIPT/'anneal_backend'),str(config),str(csvpath)],check=True)
    bits=((np.arange(4)[:,None]>>np.arange(2))&1);z=2*bits-1;E=.4*z[:,0]-.6*z[:,0]*z[:,1];dist=np.full(4,.25)
    for t in range(20):
        beta=5*(t+.5)/20;P=np.zeros((4,4))
        for s in range(4):
            for q in range(2):
                r=s^(1<<q);P[s,r]=.5/(1+math.exp(beta*(E[r]-E[s])))
            P[s,s]=1-P[s].sum()
        dist=dist@P
    observed=np.zeros(4);scores=[]
    with csvpath.open() as f:
        for row in csv.DictReader(f):
            state=row['physical_bits'];code=int(state[0])+2*int(state[1]);observed[code]+=1
    observed/=observed.sum();err=float(np.max(abs(observed-dist)))
    if err>.02:raise AssertionError('backend finite-step distribution mismatch')
    result={'status':'pass','replicas':50000,'attempts':20,'predicted_state_distribution':dist.tolist(),
            'observed_state_distribution':observed.tolist(),'max_probability_error':err,'elapsed_seconds':time.perf_counter()-start}
    (OUT/'backend_check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
