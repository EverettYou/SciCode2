import json, numpy as np
with open('/app/measurements.json') as f:
    d = json.load(f)
sts = d['measurements'][0]['spectra']
for s in sts:
    V = np.array(s['bias']); y = np.array(s['dI_dV'])
    print(f"=== panel {s['panel']}  nu={s['filling']}  T={s['temperature']}")
    # background level far away (|V|>9)
    bg = y[np.abs(V) > 9.2].mean()
    print(f"  background (|V|>9.2): {bg:.3f}")
    # smooth
    k = 9
    ys = np.convolve(y, np.ones(k)/k, mode='same')
    # gap: region where y < 0.03 contiguous near 0
    thr = 0.05
    inside = ys < thr
    # find contiguous zero region containing V closest to 0 (or near midpoint)
    i0 = np.argmin(np.abs(V - 0))
    if s['panel'] == 'd':
        print("  (no gap, metallic)")
    else:
        lo = i0
        while lo > 0 and inside[lo-1]: lo -= 1
        hi = i0
        while hi < len(V)-1 and inside[hi+1]: hi += 1
        print(f"  gap region (ys<{thr}): V from {V[lo]:.3f} to {V[hi]:.3f}, width {V[hi]-V[lo]:.3f}")
    # band edges: where ys crosses bg+0.5*(peak-bg)? better: where ys > bg + 0.1
    thr2 = bg + 0.08
    above = ys > thr2
    # segments
    segs = []
    start = None
    for i,a in enumerate(above):
        if a and start is None: start = i
        if (not a) and start is not None:
            segs.append((start, i-1)); start=None
    if start is not None: segs.append((start, len(V)-1))
    for a,b in segs:
        if b-a < 10: continue
        seg = ys[a:b+1]; Vs = V[a:b+1]
        ip = np.argmax(seg)
        print(f"  band from {Vs[0]:.3f} to {Vs[-1]:.3f} (width {Vs[-1]-Vs[0]:.3f}); peak {seg[ip]:.3f} at V={Vs[ip]:.3f}; area {np.trapz(y[a:b+1]-bg, V[a:b+1]):.3f}")
        # local maxima in segment
        from scipy.signal import find_peaks
        pk, props = find_peaks(seg, prominence=0.05)
        for p in pk:
            print(f"     local max {seg[p]:.3f} at {Vs[p]:.3f} (prominence {props['prominences'][list(pk).index(p)]:.3f})")
