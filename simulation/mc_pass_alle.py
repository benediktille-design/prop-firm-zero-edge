# -*- coding: utf-8 -*-
"""No-Edge 1:1 Coinflip – Eval-Pass fuer JEDEN 50K-Account-Typ, echte Regeln, sigma-optimiert."""
import numpy as np
rng = np.random.default_rng(2026)
START, STEPS, COST = 50_000, 32, 4*1.22
SIG=(500,1000,1500,2000,3000,4000)

# (ziel, dd, lock, intraday, TL, hart, cons_eval, min_tage)
ACC = {
 "Topstep": {
   "Standard":        (3000,2000,0,   False,1000,False,0.55,2),
   "No-Fee":          (3000,2000,0,   False,1000,False,0.55,2)},
 "Apex": {
   "Intraday":        (3000,2000,None,True, None,False,None,1),
   "EOD":             (3000,2000,100, False,1000,False,None,1)},
 "MyFundedFutures": {
   "Rapid":           (3000,2000,100, False,None,False,0.50,2),
   "Rapid EOD":       (3000,2000,100, False,None,False,0.30,2),
   "Builder":         (3000,2000,100, False,1000,False,None,1),
   "Pro":             (3000,2000,100, False,None,False,0.50,2)},
 "FundedNext": {
   "Flex":            (2500,1500,100, False,None,False,0.40,1),
   "Rapid":           (3000,2000,100, False,None,False,None,1),
   "Rapid Daily":     (3000,2000,100, False,1000,False,None,1)},
 "Tradeify": {
   "Growth":          (3000,2000,None,False,1250,False,None,1),
   "Select Flex":     (3000,2000,None,False,None,False,0.40,1),
   "Select Daily":    (3000,2000,None,False,1000,False,None,1)},
 "Lucid": {
   "Pro":             (3000,2000,100, False,1200,False,None,1),
   "Flex":            (3000,2000,100, False,1200,False,None,1),
   "Daily":           (3000,2000,100, False,1200,False,None,1)},
 "Take Profit Trader": {
   "Test":            (3000,2000,0,   False,None,False,0.50,3)},
 "FTMO": {
   "Basis":           (3000,2000,None,False,1000,False,None,1),
   "Pro":             (3000,3000,None,False,1000,True, None,1)},
}

def ein_eval(sig,ziel,dd,lock,intra,TL,hart,cons,mind):
    bal=peak=START; sd=sig/np.sqrt(STEPS); tage=0; tg=[]
    for _ in range(300):
        cum=np.cumsum(rng.normal(0,sd,STEPS))
        if TL is not None:
            if hart and cum.min()<=-TL: return False
            if not hart:
                h=np.where(cum<=-TL)[0]
                if len(h): cum=cum[:h[0]+1]
        pfad=bal+cum                         # intraday Verlauf
        if intra:                            # intraday-Trailing: Peak laeuft im Tag mit
            run=np.maximum.accumulate(np.concatenate(([peak],pfad)))
            floor_series = (run - dd) if lock is None else np.minimum(run-dd, START+lock)
            if np.any(pfad <= floor_series[1:]): return False
            peak=max(peak,pfad.max())
        else:                                # EOD-Trailing
            lo=pfad.min(); 
            floor=(peak-dd) if lock is None else min(peak-dd,START+lock)
            if min(lo,bal+cum[-1]-COST)<=floor: return False
        ende=bal+cum[-1]-COST
        pnl=ende-bal; bal=ende
        if not intra: peak=max(peak,bal)
        tage+=1; tg.append(pnl)
        if bal-START>=ziel and tage>=mind:
            if cons is not None and max(tg)>cons*(bal-START): continue
            return True
    return False

def best(cfg,n=15000):
    return max((sum(ein_eval(s,*cfg) for _ in range(n))/n*100, s) for s in SIG)

print("No-Edge 1:1 Eval-Pass, JEDER 50K-Account, echte Regeln, sigma-optimiert:\n")
for firma,accs in ACC.items():
    print(firma)
    for typ,cfg in accs.items():
        p,s=best(cfg)
        mk=[]
        if cfg[3]: mk.append("intraday-DD")
        if cfg[5]: mk.append("TL hart")
        if cfg[6]: mk.append("Cons %d%%"%(cfg[6]*100))
        print(f"   {typ:14} {p:5.1f} %  (σ{s})  {' · '.join(mk)}")
