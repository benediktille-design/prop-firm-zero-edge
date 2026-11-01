"""Gegenprobe mit FESTEM Ziel 250 $ (01.11.2026): Stop = Ziel / RR. MFF Builder + Topstep, Kosten 5 $ und 65 $."""
import os, sys
from concurrent.futures import ProcessPoolExecutor
sys.argv = ["x"]
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mc_rr.py"), encoding="utf-8").read().split("if __name__")[0])
TP = 250
FAELLE = [(rr, k) for rr in (0.2, 0.3, 0.5, 0.8, 1.0, 2.0) for k in (5.0, 65.0)]
def j(a):
    rr, k = a
    S = TP / rr
    return a, S, [sim(S, rr, k, *ACC[f][t]) for f, t in [("MyFundedFutures", "Builder"), ("Topstep", "Standard")]]
if __name__ == "__main__":
    with ProcessPoolExecutor(11) as ex:
        for (rr, k), S, r in ex.map(j, FAELLE):
            print(f"Ziel {TP}$  Stop {S:6.0f}$  ({rr}:1, Treffer {100/(1+rr):.0f}%)  Kosten {k:3.0f}$  →  MFF Builder {r[0]:5.1f}%  · Topstep {r[1]:5.1f}%", flush=True)
