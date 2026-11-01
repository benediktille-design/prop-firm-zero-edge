"""Komplett-Raster (01.11.2026): Pass-Rate je RR × Edge × Kosten × Konto. Ziel fest 250 $, Stop = 250/RR. N = 3000."""
import os, sys, itertools
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
sys.argv = ["x"]
P = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(P, "mc_edge.py"), encoding="utf-8").read().split("FAELLE")[0])
N = 3000
RR = [0.2, 0.3, 0.5, 0.8, 1.0, 2.0]; EDGE = [0.0, 0.02, 0.05]; KOSTEN = [5.0, 65.0]
KONTEN = [("MyFundedFutures", "Builder"), ("Topstep", "Standard")]
def j(a):
    rr, e, k, (f, t) = a
    S = 250 / rr; p = 1 / (1 + rr) + e
    return dict(konto=f"{f} {t}", rr=rr, edge_pkt=int(e * 100), kosten=k, stop=round(S), treffer=round(p * 100, 1),
                ev_trade=round(p * 250 - (1 - p) * S - k, 1), pass_rate=round(sim(S, rr, k, p, *ACC[f][t]), 1))
if __name__ == "__main__":
    jobs = list(itertools.product(RR, EDGE, KOSTEN, KONTEN))
    with ProcessPoolExecutor(11) as ex:
        df = pd.DataFrame(list(ex.map(j, jobs)))
    df.to_csv(os.path.join(P, "raster_rr_edge_kosten.csv"), index=False)
    for (konto, k), g in df.groupby(["konto", "kosten"]):
        print(f"\n== {konto} · Kosten {k:.0f} $/Trade · Pass-Rate % ==")
        print(g.pivot(index="edge_pkt", columns="rr", values="pass_rate").rename(index=lambda x: f"Edge +{x} Pkt").to_string())
