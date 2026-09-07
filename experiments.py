# runs the measurements for parts (c) and (d) and writes them to results/*.csv
# comparison counts are deterministic and measured once with the counting sorts.
# CPU times come from the uncounted sorts and are repeated, median reported.

import time
import statistics
from datagen import generate,SIZES
from hybrid import hybrid,mergesort,hybrid_nc,mergesort_nc

S_FIXED=8

def cpu(fn,arr,repeat):
    ts=[]
    for _ in range(repeat):
        t=time.process_time()
        out=fn(arr)
        ts.append(time.process_time()-t)
        del out
    return statistics.median(ts),min(ts)

def repeats_for(n):
    if n<=10000: return 7
    if n<=200000: return 5
    if n<=2000000: return 3
    return 2

def part_c_i(S=S_FIXED,seed=0,out="results/c_i_comparisons_over_n.csv"):
    print("(c)(i) comparisons and CPU over n, S=%d"%S,flush=True)
    f=open(out,"w")
    f.write("n,hybrid_cmps,merge_cmps,hybrid_cpu_med,merge_cpu_med,hybrid_cpu_min,merge_cpu_min,repeats\n")
    print("%10s %14s %14s %10s %10s %9s"%("n","hybrid cmps","merge cmps","hyb cpu","mrg cpu","speedup"),flush=True)
    for n in SIZES:
        a=generate(n,seed)
        r=repeats_for(n)
        hc=hybrid(a,S)[1]
        mc=mergesort(a)[1]
        ht,hmin=cpu(lambda x:hybrid_nc(x,S),a,r)
        mt,mmin=cpu(mergesort_nc,a,r)
        f.write("%d,%d,%d,%.6f,%.6f,%.6f,%.6f,%d\n"%(n,hc,mc,ht,mt,hmin,mmin,r))
        f.flush()
        print("%10d %14d %14d %10.4f %10.4f %8.2fx"%(n,hc,mc,ht,mt,mt/ht),flush=True)
        del a
    f.close()
    print("wrote",out,flush=True)

CONFIG=[
    (10000,   [1,2,3,4,6,8,12,16,24,32,48,64,96,128],7),
    (100000,  [1,2,3,4,6,8,12,16,24,32,48,64,96,128],5),
    (1000000, [1,2,4,6,8,12,16,24,32,48,64,128],3),
    (10000000,[2,4,8,16,32,64],2),
]

def part_c_iii(seed=0,out="results/c_iii_optimal_S.csv"):
    print("\n(c)(iii) optimal S at several n",flush=True)
    f=open(out,"w")
    f.write("n,S,key_comparisons,cpu_median_s,cpu_min_s,repeats\n")
    for n,grid,r in CONFIG:
        a=generate(n,seed)
        mc=mergesort(a)[1]
        mt,mmin=cpu(mergesort_nc,a,r)
        f.write("%d,merge,%d,%.6f,%.6f,%d\n"%(n,mc,mt,mmin,r))
        rows=[]
        for S in grid:
            c=hybrid(a,S)[1]
            t,tmin=cpu(lambda x:hybrid_nc(x,S),a,r)
            f.write("%d,%d,%d,%.6f,%.6f,%d\n"%(n,S,c,t,tmin,r))
            f.flush()
            rows.append((S,c,t))
        best=min(rows,key=lambda x:x[2])
        print("  n=%-9d best S=%-4d %.4fs (merge %.4fs, %.2fx)  fewest cmps at S=%d"%(
              n,best[0],best[2],mt,mt/best[2],min(rows,key=lambda x:x[1])[0]),flush=True)
        del a
    f.close()
    print("wrote",out,flush=True)

def part_d(S,seed=0,n=10000000,out="results/d_10M_headtohead.csv"):
    print("\n(d) head to head at n=%d, S=%d"%(n,S),flush=True)
    a=generate(n,seed)
    hc=hybrid(a,S)[1]
    mc=mergesort(a)[1]
    ht,hmin=cpu(lambda x:hybrid_nc(x,S),a,3)
    mt,mmin=cpu(mergesort_nc,a,3)
    ok=hybrid_nc(a,S)==mergesort_nc(a)
    with open(out,"w") as f:
        f.write("algorithm,S,key_comparisons,cpu_median_s,cpu_min_s\n")
        f.write("hybrid,%d,%d,%.6f,%.6f\n"%(S,hc,ht,hmin))
        f.write("mergesort,,%d,%.6f,%.6f\n"%(mc,mt,mmin))
    print("  hybrid    %d cmps  %.3fs"%(hc,ht),flush=True)
    print("  mergesort %d cmps  %.3fs"%(mc,mt),flush=True)
    print("  hybrid uses %+.2f%% comparisons and %+.2f%% CPU time"%(
          100*(hc-mc)/mc,100*(ht-mt)/mt),flush=True)
    print("  outputs identical:",ok,flush=True)
    print("wrote",out,flush=True)

if __name__=="__main__":
    t0=time.perf_counter()
    part_c_i()
    part_c_iii()
    part_d(S=8)
    print("\ntotal %.0fs"%(time.perf_counter()-t0),flush=True)
