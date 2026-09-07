# figures for part (c)
# the two measures live on different scales, so they get one panel each.
# never a twin y-axis: it lets the reader "see" a crossover that is an
# artefact of where the two scales were pinned.

import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

SURFACE="#fcfcfb"
INK="#0b0b0b"
INK2="#52514e"
GRID="#e3e2dd"
SERIES="#2a78d6"
BASE="#8a8983"
BAND="#e8f0fc"
SERIES2="#eb6834"

def style():
    sns.set_theme(style="ticks")
    plt.rcParams.update({
        "figure.facecolor":SURFACE,
        "axes.facecolor":SURFACE,
        "axes.edgecolor":GRID,
        "axes.labelcolor":INK2,
        "text.color":INK,
        "xtick.color":INK2,
        "ytick.color":INK2,
        "font.size":10,
        "axes.titlesize":11,
        "axes.grid":True,
        "grid.color":GRID,
        "grid.linewidth":0.8,
        "savefig.facecolor":SURFACE,
    })

def load(path):
    rows=list(csv.DictReader(open(path)))
    merge=[r for r in rows if r["S"]=="merge"][0]
    data=[r for r in rows if r["S"]!="merge"]
    S=[int(r["S"]) for r in data]
    cmps=[int(r["key_comparisons"])/1e6 for r in data]
    cpu=[float(r["cpu_median_s"]) for r in data]
    leaf=[r["leaf_sizes"] for r in data]
    return S,cmps,cpu,leaf,int(merge["key_comparisons"])/1e6,float(merge["cpu_median_s"])

def plot_S(path="results/S_sweep_n1000000.csv",out="results/S_sweep_n1000000.png",n=1000000):
    S,cmps,cpu,leaf,m_cmps,m_cpu=load(path)
    best=min(range(len(cpu)),key=lambda i:cpu[i])
    band=[i for i in range(len(cpu)) if cpu[i]<=cpu[best]*1.01]
    lo,hi=S[band[0]],S[band[-1]]

    style()
    fig,(ax1,ax2)=plt.subplots(2,1,figsize=(8.4,7.6),sharex=True)

    for ax in (ax1,ax2):
        ax.axvspan(lo,hi,color=BAND,zorder=0,lw=0)
        ax.set_xscale("log",base=2)
        ax.set_yscale("log")
        sns.despine(ax=ax)

    ax1.axhline(m_cmps,color=BASE,ls="--",lw=1.5,zorder=1)
    ax1.plot(S,cmps,color=SERIES,lw=2,marker="o",ms=5.5,zorder=3,
             markeredgecolor=SURFACE,markeredgewidth=1.2)
    ax1.set_ylabel("key comparisons (millions)")
    ax1.set_title("Key comparisons only ever rise with S",loc="left",color=INK,pad=26)
    ax1.set_yticks([20,30,50,80,130])
    ax1.set_ylim(16,190)
    ax1.text(430,m_cmps*1.05,"plain merge sort  %.1fM"%m_cmps,
             color=BASE,fontsize=9,va="bottom",ha="right")
    # one label per plateau shown, enough to make the step structure readable
    for i,dx,dy,ha in ((0,0,13,"center"),(6,0,13,"center"),(13,0,13,"center"),
                       (18,0,13,"center"),(21,-10,-4,"right")):
        ax1.annotate("leaf %s"%leaf[i],(S[i],cmps[i]),textcoords="offset points",
                     xytext=(dx,dy),ha=ha,fontsize=8.5,color=INK2)

    ax2.axhline(m_cpu,color=BASE,ls="--",lw=1.5,zorder=1)
    ax2.plot(S,cpu,color=SERIES,lw=2,marker="o",ms=5.5,zorder=3,
             markeredgecolor=SURFACE,markeredgewidth=1.2)
    ax2.set_ylabel("CPU time, median of 5 (s)")
    ax2.set_xlabel("S   (switch to insertion sort once a subarray is <= S)")
    ax2.set_title("CPU time dips, but the whole band S=%d..%d is one flat optimum"%(lo,hi),
                  loc="left",color=INK,pad=10)
    ax2.set_yticks([1.4,2,3,4,5,7])
    ax2.set_ylim(1.25,8.2)
    ax2.text(430,m_cpu*1.06,"plain merge sort  %.2fs"%m_cpu,
             color=BASE,fontsize=9,va="bottom",ha="right")
    ax2.annotate("%.2fs"%cpu[best],(S[best],cpu[best]),textcoords="offset points",
                 xytext=(-11,7),ha="right",fontsize=9,color=SERIES)

    ticks=[1,2,4,8,16,32,64,128,256,512]
    ax2.set_xticks(ticks)
    ax2.set_xticklabels([str(t) for t in ticks])
    ax2.set_xlim(0.82,700)
    for ax in (ax1,ax2):
        ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax.grid(True,which="major",color=GRID,lw=0.8)

    ax1.text((lo*hi)**0.5,178,"fastest band  S=%d..%d"%(lo,hi),
             fontsize=8.5,color=SERIES,va="top",ha="center")

    fig.suptitle("Hybrid merge sort, n = %s: the two metrics disagree"%format(n,","),
                 x=0.010,ha="left",fontsize=13,color=INK,weight="semibold")
    fig.tight_layout(rect=[0,0,1,0.962])
    fig.savefig(out,dpi=200)
    print("wrote",out)

if __name__=="__main__":
    plot_S()

def _model():
    from functools import lru_cache
    def H(m): return sum(1.0/k for k in range(1,m+1))
    def I(m): return m*(m-1)/4.0+m-H(m)
    def M(a,b): return a+b-a/(b+1.0)-b/(a+1.0)
    @lru_cache(None)
    def HYB(m,S):
        if m<=S: return I(m)
        lo=m//2
        return HYB(lo,S)+HYB(m-lo,S)+M(lo,m-lo)
    return HYB

def plot_n(path="results/c_i_comparisons_over_n.csv",out="results/c_i_over_n.svg",S=8):
    rows=list(csv.DictReader(open(path)))
    n=[int(r["n"]) for r in rows]
    hc=[int(r["hybrid_cmps"]) for r in rows]
    mc=[int(r["merge_cmps"]) for r in rows]
    ht=[float(r["hybrid_cpu_med"]) for r in rows]
    mt=[float(r["merge_cpu_med"]) for r in rows]
    HYB=_model()
    mh=[HYB(x,S)/x for x in n]
    mm=[HYB(x,1)/x for x in n]

    style()
    fig,(ax1,ax2)=plt.subplots(2,1,figsize=(8.4,7.4),sharex=True)
    for ax in (ax1,ax2):
        ax.set_xscale("log")
        sns.despine(ax=ax)
        ax.grid(True,which="major",color=GRID,lw=0.8)
        ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())

    ax1.plot(n,mh,color=SERIES,lw=2,zorder=2)
    ax1.plot(n,mm,color=SERIES2,lw=2,zorder=2)
    ax1.plot(n,[c/x for c,x in zip(hc,n)],ls="none",marker="o",ms=7,color=SERIES,
             markeredgecolor=SURFACE,markeredgewidth=1.4,zorder=3)
    ax1.plot(n,[c/x for c,x in zip(mc,n)],ls="none",marker="s",ms=6.5,color=SERIES2,
             markeredgecolor=SURFACE,markeredgewidth=1.4,zorder=3)
    ax1.set_ylabel("key comparisons per element,  C(n) / n")
    ax1.set_title("Comparisons per element grow linearly in log n, so C(n) = Θ(n log n)",
                  loc="left",color=INK,pad=10)
    ax1.annotate("hybrid, S=%d"%S,(n[-1],mh[-1]),textcoords="offset points",
                 xytext=(-6,7),ha="right",fontsize=9.5,color=SERIES)
    ax1.annotate("plain merge sort",(n[-2],mm[-2]),textcoords="offset points",
                 xytext=(4,-15),ha="left",fontsize=9.5,color=SERIES2)
    ax1.text(n[0],max(mh)*0.99,"lines = average-case model    markers = measured",
             fontsize=8.5,color=INK2,va="top")

    ax2.plot(n,[a/b for a,b in zip(mt,ht)],color=SERIES,lw=2,marker="o",ms=6,
             markeredgecolor=SURFACE,markeredgewidth=1.3)
    ax2.axhline(1.0,color=BASE,ls="--",lw=1.5)
    ax2.set_ylabel("speedup in CPU time")
    ax2.set_xlabel("n")
    ax2.set_title("The CPU-time advantage shrinks as n grows",loc="left",color=INK,pad=10)
    ax2.set_ylim(0.98,1.45)
    ax2.text(n[-1],1.005,"no gain",color=BASE,fontsize=9,ha="right",va="bottom")
    fig.tight_layout()
    fig.savefig(out)
    print("wrote",out)

def plot_optimal(path="results/c_iii_optimal_S.csv",out="results/c_iii_optimal_S.svg"):
    rows=list(csv.DictReader(open(path)))
    ns=sorted(set(int(r["n"]) for r in rows))
    style()
    fig,ax=plt.subplots(figsize=(8.4,4.9))
    colors=[SERIES,SERIES2,"#1baf7a","#4a3aa7"]
    sns.despine(ax=ax)
    for k,n in enumerate(ns):
        sub=[r for r in rows if int(r["n"])==n]
        base=float([r for r in sub if r["S"]=="merge"][0]["cpu_median_s"])
        pts=sorted((int(r["S"]),float(r["cpu_median_s"])) for r in sub if r["S"]!="merge")
        S=[p[0] for p in pts]; rel=[base/p[1] for p in pts]
        c=colors[k%len(colors)]
        ax.plot(S,rel,lw=2,marker="o",ms=6,color=c,label="n = %s"%format(n,","),
                markeredgecolor=SURFACE,markeredgewidth=1.3)
        # label at the right end, where the four lines are furthest apart
        ax.annotate("n = %s"%format(n,","),(S[-1],rel[-1]),textcoords="offset points",
                    xytext=(9,-3),ha="left",fontsize=9,color=c)
        b=max(range(len(rel)),key=lambda i:rel[i])
        ax.plot([S[b]],[rel[b]],marker="o",ms=11,mfc="none",mec=c,mew=1.8,ls="none")
    ax.axhline(1.0,color=BASE,ls="--",lw=1.5)
    ax.set_xscale("log",base=2)
    ticks=[1,2,4,8,16,32,64,128]
    ax.set_xticks(ticks); ax.set_xticklabels([str(t) for t in ticks])
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.grid(True,which="major",color=GRID,lw=0.8)
    ax.set_xlabel("S")
    ax.set_ylabel("speedup over plain merge sort")
    ax.set_title("The best S lands in the same place at every size",loc="left",color=INK,pad=10)
    ax.set_xlim(0.85,330)
    ax.text(300,1.005,"plain merge sort",color=BASE,fontsize=9,va="bottom",ha="right")
    ax.text(1.05,0.72,"rings mark the fastest S for each n",fontsize=8.5,color=INK2)
    fig.tight_layout()
    fig.savefig(out)
    print("wrote",out)
