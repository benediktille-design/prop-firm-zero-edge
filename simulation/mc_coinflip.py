# -*- coding: utf-8 -*-
"""No-Edge 1:1 Coinflip: jeder Trade 50/50 TP oder SL, feste Groesse, echte Regeln je 50K-Account."""
import numpy as np, sys
src = open(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "mc_pass_alle.py"), encoding="utf-8").read().split("def ein_eval")[0]
exec(src)                                   # holt ACC (Regeln) + START
rng = np.random.default_rng(2026)
KOSTEN, TRADES_TAG, TICKS, N = 5.0, 2, 4, 10000

def sim(R, ziel, dd, lock, intra, TL, hart, cons, mind):
    bal = np.full(N, START, float); peak = bal.copy()
    best = np.zeros(N); done = np.zeros(N, bool); ok = np.zeros(N, bool)
    tick = R / TICKS
    for tag in range(300):
        if done.all(): break
        dp = np.zeros(N); stop = done.copy()
        for _ in range(TRADES_TAG):
            idx = np.where(~stop & ~done)[0]
            opn = np.zeros(len(idx))
            while len(idx):
                opn += np.where(rng.random(len(idx)) < .5, tick, -tick)
                eq = bal[idx] + opn
                if intra: peak[idx] = np.maximum(peak[idx], eq)
                fl = peak[idx] - dd if lock is None else np.minimum(peak[idx] - dd, START + lock)
                aus = eq <= fl                                  # DD gerissen -> Fail
                done[idx[aus]] = True
                tl = np.zeros(len(idx), bool)
                if TL is not None:
                    tl = ~aus & (dp[idx] + opn <= -TL)
                    if hart: done[idx[tl]] = True               # hartes Limit -> Fail
                    else: stop[idx[tl]] = True                  # weich -> Tag vorbei
                fertig = ~aus & (np.abs(opn) >= R)
                zu = fertig | (tl & (not hart))                 # Trade schliesst
                j = idx[zu]
                bal[j] += opn[zu] - KOSTEN; dp[j] += opn[zu] - KOSTEN
                weg = aus | tl | fertig
                idx, opn = idx[~weg], opn[~weg]
            # nach dem Trade: bestanden?
            gew = bal - START; bt = np.maximum(best, dp)
            p = ~done & (gew >= ziel)
            if cons is not None: p &= bt <= cons * gew
            ok |= p; done |= p
        best = np.maximum(best, dp)
        if not intra: peak = np.maximum(peak, bal)
    return ok.mean() * 100

if __name__ == "__main__":
    print(f"No-Edge 1:1 Coinflip · {TRADES_TAG} Trades/Tag · {N} Laeufe · Kosten {KOSTEN}$/Trade\n")
    print(f"{'Account':32} {'±250$':>7} {'±500$':>7}")
    for firma, accs in ACC.items():
        for typ, cfg in accs.items():
            a = sim(250, *cfg); b = sim(500, *cfg)
            print(f"{firma+' '+typ:32} {a:6.1f}% {b:6.1f}%", flush=True)
