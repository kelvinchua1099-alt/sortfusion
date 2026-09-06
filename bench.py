# timing harness for parts (c) and (d)
# process_time() is CPU time, which is what the assignment asks for.
# comparison counts are deterministic for a given array and S, so they are
# measured once. only the timings are repeated, and the median is reported
# because a single run picks up whatever else the machine was doing.

import time
import sys
import statistics
from datagen import generate,SIZES
from hybrid import hybrid,mergesort

S_DEFAULT=16

S_GRID=[1,2,3,4,5,6,8,10,12,14,16,20,24,32,40,48,64,96,128,192,256,512]

def leafsizes(n,S):
    # the subarray sizes insertion sort actually receives.
    # only two distinct sizes exist per level, so this stays O(log n).
    seen=set()
    out=set()
    stack=[n]
    while stack:
        m=stack.pop()
        if m in seen:
            continue
        seen.add(m)
        if m<=S:
            out.add(m)
        else:
            mid=m//2
            stack.append(mid)
            stack.append(m-mid)
    return sorted(out)

def runtimes(fn,arr,repeat):
    times=[]
    count=0
    for _ in range(repeat):
        c0=time.process_time()
        out,count=fn(arr)
        times.append(time.process_time()-c0)
        del out
    return count,times

def repeats_for(n):
    if n<=10000:
        return 5
    if n<=200000:
        return 3
    return 1

def sweep_n(sizes,S=S_DEFAULT,seed=0):
    print("comparisons and CPU time over n, S=%d"%S)
    print("%10s %14s %10s %14s %10s %9s"%("n","hybrid cmps","cpu s","merge cmps","cpu s","speedup"))
    for n in sizes:
        a=generate(n,seed)
        r=repeats_for(n)
        hc,ht=runtimes(lambda x:hybrid(x,S),a,r)
        mc,mt=runtimes(mergesort,a,r)
        ht=min(ht)
        mt=min(mt)
        print("%10d %14d %10.4f %14d %10.4f %8.2fx"%(n,hc,ht,mc,mt,mt/ht))
        del a

def sweep_S(n,values=None,seed=0,repeat=5,csv=None):
    if values is None:
        values=S_GRID
    a=generate(n,seed)
    mc,mt=runtimes(mergesort,a,repeat)
    m_med=statistics.median(mt)

    print("n=%d, seed=%d, %d timing repeats per row"%(n,seed,repeat))
    print("plain merge sort: %d comparisons, %.4fs median CPU\n"%(mc,m_med))
    head="%5s %12s %14s %8s %10s %10s %9s"%("S","leaf sizes","key cmps","vs merge","cpu med s","cpu min s","speedup")
    print(head)
    print("-"*len(head))
    rows=[]
    prev=None
    for S in values:
        c,t=runtimes(lambda x:hybrid(x,S),a,repeat)
        med=statistics.median(t)
        ls=leafsizes(n,S)
        lab="%d-%d"%(ls[0],ls[-1]) if len(ls)>1 else str(ls[0])
        # rows sharing a comparison count are the same algorithm, separate them
        if prev is not None and c!=prev:
            print("- "*(len(head)//2))
        prev=c
        rows.append((S,lab,c,c/mc,med,min(t),m_med/med))
        print("%5d %12s %14d %7.2fx %10.4f %10.4f %8.2fx"%(S,lab,c,c/mc,med,min(t),m_med/med))
    del a

    best=min(rows,key=lambda r:r[4])
    spread=[r for r in rows if r[4]<=best[4]*1.01]
    print("\nfastest S=%d (leaf %s) at %.4fs"%(best[0],best[1],best[4]))
    print("within 1%% of it: S in %s"%[r[0] for r in spread])
    print("  those cover leaf sizes %s"%sorted(set(r[1] for r in spread)))
    fewest=min(rows,key=lambda r:r[2])
    print("fewest comparisons: S=%d at %d"%(fewest[0],fewest[2]))

    if csv:
        with open(csv,"w") as f:
            f.write("S,leaf_sizes,key_comparisons,ratio_vs_merge,cpu_median_s,cpu_min_s,speedup_vs_merge\n")
            for r in rows:
                f.write("%d,%s,%d,%.6f,%.6f,%.6f,%.6f\n"%r)
            f.write("merge,1,%d,1.0,%.6f,%.6f,1.0\n"%(mc,m_med,min(mt)))
        print("wrote %s"%csv)
    return rows

if __name__=="__main__":
    if "table" in sys.argv:
        sweep_S(1000000,repeat=5,csv="results/S_sweep_n1000000.csv")
    elif "quick" in sys.argv:
        sweep_n([n for n in SIZES if n<=200000])
        sweep_S(100000,repeat=3)
    else:
        sweep_n(SIZES)
        sweep_S(1000000,repeat=5,csv="results/S_sweep_n1000000.csv")
