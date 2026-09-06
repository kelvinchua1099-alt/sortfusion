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
