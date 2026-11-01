"""Pass-Rate MIT kleiner Edge (01.11.2026): festes Ziel 250 $, Stop = 250/RR. Edge = Trefferquote X Prozentpunkte über Break-even.
Preis = Zufallsweg mit leichter Schieflage q, so gewählt, dass P(Ziel vor Stop) = gewünschte Trefferquote."""
import os, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy.optimize import brentq
sys.argv = ["x"]
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mc_rr.py"), encoding="utf-8").read().split("def sim")[0])
TP = 250

def treffer(q, a, b):            # a = Stop in Ticks, b = Ziel in Ticks
    if abs(q - .5) < 1e-12: return a / (a + b)
    r = (1 - q) / q
    return (1 - r ** a) / (1 - r ** (a + b))

def sim(S, rr, kosten, p_ziel, ziel, dd, lock, intra, TL, hart, cons, mind, seed=1):
    rng = np.random.default_rng(seed); T = rr * S
    tick = S / 20 if rr >= 0.5 else T / 4
    a, b = round(S / tick), round(T / tick)
    q = brentq(lambda x: treffer(x, a, b) - p_ziel, 0.3, 0.7)
    bal = np.full(N, START, float); peak = bal.copy(); best = np.zeros(N)
    done = np.zeros(N, bool); ok = np.zeros(N, bool); tage = np.zeros(N)
    for tag in range(300):
        if done.all(): break
        dp = np.zeros(N); stop = done.copy()
        for _ in range(TRADES_TAG):
            idx = np.where(~stop & ~done)[0]; opn = np.zeros(len(idx))
            while len(idx):
                opn += np.where(rng.random(len(idx)) < q, tick, -tick)
                eq = bal[idx] + opn
                if intra: peak[idx] = np.maximum(peak[idx], eq)
                fl = peak[idx] - dd if lock is None else np.minimum(peak[idx] - dd, START + lock)
                aus = eq <= fl; done[idx[aus]] = True
                tl = np.zeros(len(idx), bool)
                if TL is not None:
                    tl = ~aus & (dp[idx] + opn <= -TL)
                    if hart: done[idx[tl]] = True
                    else: stop[idx[tl]] = True
                fertig = ~aus & ((opn >= T - 1e-9) | (opn <= -S + 1e-9))
                zu = fertig | (tl & (not hart)); j = idx[zu]
                bal[j] += opn[zu] - kosten; dp[j] += opn[zu] - kosten
                weg = aus | tl | fertig; idx, opn = idx[~weg], opn[~weg]
            gew = bal - START; bt = np.maximum(best, dp)
            p = ~done & (gew >= ziel) & (tage + 1 >= mind)
            if cons is not None: p &= bt <= cons * gew
            ok |= p; done |= p
        best = np.maximum(best, dp); tage += ~done
        if not intra: peak = np.maximum(peak, bal)
    return ok.mean() * 100

FAELLE = [(rr, e) for rr in (0.2, 0.5, 1.0) for e in (0.0, 0.02, 0.05)]
def j(a):
    rr, e = a; S = TP / rr; p = 1 / (1 + rr) + e
    ev = p * TP - (1 - p) * S - 5
    return a, S, p, ev, sim(S, rr, 5.0, p, *ACC["MyFundedFutures"]["Builder"])
if __name__ == "__main__":
    with ProcessPoolExecutor(9) as ex:
        for (rr, e), S, p, ev, r in ex.map(j, FAELLE):
            print(f"{rr}:1  Ziel {TP}$ Stop {S:5.0f}$  Edge +{e*100:.0f} Pkt → Treffer {p*100:4.1f}%  EV/Trade {ev:+6.1f}$  →  MFF Builder Pass {r:5.1f}%", flush=True)
