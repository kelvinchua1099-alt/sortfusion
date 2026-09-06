# timing harness for parts (c) and (d)
# process_time() is CPU time, which is what the assignment asks for.
# perf_counter() wall time is also recorded so we can tell if the machine
# was doing something else during a run.

import time
import sys
from datagen import generate,SIZES
from hybrid import hybrid,mergesort

S_DEFAULT=16

def timeit(fn,arr,repeat=1):
    best_cpu=None
    best_wall=None
    count=0
    for _ in range(repeat):
        c0=time.process_time()
        w0=time.perf_counter()
        out,count=fn(arr)
        cpu=time.process_time()-c0
        wall=time.perf_counter()-w0
        del out
        if best_cpu is None or cpu<best_cpu:
            best_cpu=cpu
            best_wall=wall
    return count,best_cpu,best_wall

def repeats_for(n):
    if n<=10000:
        return 5
    if n<=200000:
        return 3
    return 1

def sweep_n(sizes,S=S_DEFAULT,seed=0):
    print("comparisons and CPU time over n, S=%d"%S)
    print("%10s %14s %10s %14s %10s %9s"%("n","hybrid cmps","cpu s","merge cmps","cpu s","speedup"))
    rows=[]
    for n in sizes:
        a=generate(n,seed)
        r=repeats_for(n)
        hc,ht,hw=timeit(lambda x:hybrid(x,S),a,r)
        mc,mt,mw=timeit(mergesort,a,r)
        speed=mt/ht if ht>0 else float("nan")
        print("%10d %14d %10.4f %14d %10.4f %8.2fx"%(n,hc,ht,mc,mt,speed))
        rows.append((n,hc,ht,mc,mt))
        del a
    return rows

def sweep_S(n,values,seed=0):
    print("\ncomparisons and CPU time over S, n=%d"%n)
    print("%6s %14s %10s"%("S","cmps","cpu s"))
    a=generate(n,seed)
    mc,mt,mw=timeit(mergesort,a,1)
    rows=[]
    for S in values:
        c,t,w=timeit(lambda x:hybrid(x,S),a,1)
        print("%6d %14d %10.4f"%(S,c,t))
        rows.append((S,c,t))
    print("%6s %14d %10.4f   <- plain merge sort"%("-",mc,mt))
    del a
    return rows

if __name__=="__main__":
    quick="quick" in sys.argv
    if quick:
        sizes=[n for n in SIZES if n<=200000]
        big=100000
    else:
        sizes=SIZES
        big=1000000
    t0=time.perf_counter()
    sweep_n(sizes)
    sweep_S(big,[1,2,4,8,16,32,64,128,256,512])
    print("\ntotal %.1fs"%(time.perf_counter()-t0))
