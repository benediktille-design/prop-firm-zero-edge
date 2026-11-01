"""Figures for the paper (data: own Monte-Carlo output)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

H = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

# Fig 1: fixed stop $250, target = RR x stop (typical EOD account)
rr = [0.1, 0.2, 0.3, 0.5, 1.0, 2.0, 3.0]
mit = [0.2, 4.6, 10.0, 14.1, 20.3, 23.0, 24.2]
ohne = [10.9, 21.5, 24.1, 25.6, 27.5, 26.8, 27.3]
fig, ax = plt.subplots(figsize=(5.2, 2.8))
ax.plot(rr, ohne, "o-", color="0.55", label="no costs")
ax.plot(rr, mit, "o-", color="black", label="$5 costs per trade")
ax.axhline(40, ls="--", lw=0.8, color="0.3"); ax.text(3.0, 41, "static-DD bound 40%", ha="right", fontsize=8)
ax.set_xscale("log"); ax.set_xticks(rr); ax.set_xticklabels([str(r) for r in rr]); ax.minorticks_off()
ax.set_xlabel("reward : risk (stop fixed at $250)"); ax.set_ylabel("pass rate (%)"); ax.set_ylim(0, 45)
ax.legend(frameon=False, loc="lower right"); fig.tight_layout(); fig.savefig(os.path.join(H, "figures", "fig1_fixed_stop.png"), dpi=200)

# Fig 2: fixed target $250, edge x RR, $5 costs (MFF Builder)
d = pd.read_csv(os.path.join(H, "data", "raster_rr_edge_kosten.csv"))
d = d[(d.konto == "MyFundedFutures Builder") & (d.kosten == 5.0)]
fig, ax = plt.subplots(figsize=(5.2, 2.8))
for e, c, lab in [(0, "0.65", "no edge"), (2, "0.4", "+2 pp hit rate"), (5, "black", "+5 pp hit rate")]:
    x = d[d.edge_pkt == e].sort_values("rr")
    ax.plot(x.rr, x.pass_rate, "o-", color=c, label=lab)
ax.set_xscale("log"); ax.set_xticks([0.2, 0.3, 0.5, 0.8, 1, 2]); ax.set_xticklabels(["0.2", "0.3", "0.5", "0.8", "1", "2"]); ax.minorticks_off()
ax.set_xlabel("reward : risk (target fixed at $250)"); ax.set_ylabel("pass rate (%)"); ax.set_ylim(0, 70)
ax.legend(frameon=False, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.12)); fig.tight_layout(); fig.savefig(os.path.join(H, "figures", "fig2_edge_grid.png"), dpi=200)

# Fig 3: coin-flip 1:1, fixed size, per account
acc = ["Topstep Std", "Apex Intraday", "Apex EOD", "MFF Rapid", "MFF Builder", "FundedNext Flex", "Tradeify Growth",
       "Lucid Flex", "Take Profit Trader", "FTMO Basis", "FTMO Pro"]
p250 = [20.6, 17.1, 20.0, 20.6, 19.5, 19.6, 18.7, 20.2, 20.5, 19.3, 29.2]
p500 = [24.9, 18.3, 25.1, 26.1, 25.2, 23.4, 22.9, 25.6, 25.5, 23.1, 8.4]
fig, ax = plt.subplots(figsize=(5.6, 3.2)); y = range(len(acc))
ax.barh([i + 0.2 for i in y], p250, 0.4, color="0.7", label="±$250 per trade")
ax.barh([i - 0.2 for i in y], p500, 0.4, color="black", label="±$500 per trade")
ax.set_yticks(list(y)); ax.set_yticklabels(acc); ax.invert_yaxis(); ax.axvline(40, ls="--", lw=0.8, color="0.3")
ax.set_xlabel("pass rate (%)"); ax.legend(frameon=False, loc="upper right", fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(H, "figures", "fig3_accounts.png"), dpi=200)
