import json, numpy as np
D = json.load(open('/app/measurements.json'))['measurements']
def sts(panel):
    for s in D[0]['spectra']:
        if s['panel']==panel:
            return np.array(s['bias']), np.array(s['dI_dV'])
def nmr(f):
    for s in D[1]['samples']:
        if s['filling']==f:
            return np.array(s['temperature']), np.array(s['one_over_T1']), np.array(s['uncertainty'])
def res(f):
    for s in D[2]['samples']:
        if s['filling']==f:
            return np.array(s['temperature']), np.array(s['resistivity']), np.array(s['uncertainty'])
