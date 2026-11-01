# -*- coding: utf-8 -*-
"""No-Edge Pass-Rate je Chance-Risiko-Verhältnis (01.11.2026).
Preis = fairer Zufallsweg in Ticks → Trade trifft Ziel mit Wahrscheinlichkeit Stop/(Stop+Ziel) (kein Vorteil, EV vor Kosten = 0).
Stop fest 250 $ (bzw. 500 $), Ziel = RR × Stop, 2 Trades/Tag, echte Eval-Regeln je 50K-Konto (ACC aus mc_pass_alle.py).
Gerechnet mit 5 $ Kosten/Trade UND ohne Kosten (zeigt, wie stark Kosten bei kleinem RR zuschlagen)."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

P = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(P, "mc_pass_alle.py"), encoding="utf-8").read().split("def ein_eval")[0]
exec(src)                                   # ACC + START
N, TRADES_TAG = 4000, 2
RRS = [0.1, 0.2, 0.3, 0.5, 1.0, 2.0, 3.0]


def sim(S, rr, kosten, ziel, dd, lock, intra, TL, hart, cons, mind, seed=1):
    rng = np.random.default_rng(seed)
    T = rr * S
    tick = S / 20 if rr >= 0.5 else T / 4          # Ziel immer ≥ 4 Ticks, Stop Vielfaches davon
    bal = np.full(N, START, float); peak = bal.copy()
    best = np.zeros(N); done = np.zeros(N, bool); ok = np.zeros(N, bool); tage = np.zeros(N)
    for tag in range(300):
        if done.all():
            break
        dp = np.zeros(N); stop = done.copy()
        for _ in range(TRADES_TAG):
            idx = np.where(~stop & ~done)[0]
            opn = np.zeros(len(idx))
            while len(idx):
                opn += np.where(rng.random(len(idx)) < .5, tick, -tick)
                eq = bal[idx] + opn
                if intra:
                    peak[idx] = np.maximum(peak[idx], eq)
                fl = peak[idx] - dd if lock is None else np.minimum(peak[idx] - dd, START + lock)
                aus = eq <= fl
                done[idx[aus]] = True
                tl = np.zeros(len(idx), bool)
                if TL is not None:
                    tl = ~aus & (dp[idx] + opn <= -TL)
                    if hart:
                        done[idx[tl]] = True
                    else:
                        stop[idx[tl]] = True
                fertig = ~aus & ((opn >= T - 1e-9) | (opn <= -S + 1e-9))
                zu = fertig | (tl & (not hart))
                j = idx[zu]
                bal[j] += opn[zu] - kosten; dp[j] += opn[zu] - kosten
                weg = aus | tl | fertig
                idx, opn = idx[~weg], opn[~weg]
            gew = bal - START; bt = np.maximum(best, dp)
            p = ~done & (gew >= ziel) & (tage + 1 >= mind)
            if cons is not None:
                p &= bt <= cons * gew
            ok |= p; done |= p
        best = np.maximum(best, dp); tage += ~done
        if not intra:
            peak = np.maximum(peak, bal)
    return ok.mean() * 100


def job(a):
    firma, typ, S = a
    cfg = ACC[firma][typ]
    return firma, typ, S, [sim(S, rr, 5.0, *cfg) for rr in RRS], [sim(S, rr, 0.0, *cfg) for rr in RRS]


if __name__ == "__main__":
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 250
    jobs = [(f, t, S) for f, a in ACC.items() for t in a]
    kopf = " ".join(f"{r:>6}" for r in RRS)
    print(f"No-Edge Pass-Rate (%) · Stop {S} $ · 2 Trades/Tag · N={N}\nRR (Ziel:Stop)          {kopf}")
    with ProcessPoolExecutor(max(1, os.cpu_count() - 1)) as ex:
        for firma, typ, S, mk, ok in ex.map(job, jobs):
            print(f"{(firma + ' ' + typ)[:22]:22} mit Kosten  " + " ".join(f"{x:6.1f}" for x in mk), flush=True)
            print(f"{'':22} ohne Kosten " + " ".join(f"{x:6.1f}" for x in ok), flush=True)
