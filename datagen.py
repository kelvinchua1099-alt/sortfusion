# part (b): random datasets of increasing size, 1000 up to 10 million
# values are integers in [1,x], x defaults to MAXVALUE
# arrays are rebuilt from the seed instead of being stored on disk,
# a 10 million element array is about 400MB in memory but only a seed on paper

import random

try:
    import numpy as np
except ImportError:
    np=None

MAXVALUE=10000000

SIZES=[1000,2000,5000,10000,20000,50000,100000,200000,500000,1000000,2000000,5000000,10000000]

def generate(n,seed=0,x=MAXVALUE):
    if np is not None:
        return np.random.default_rng(seed).integers(1,x+1,n).tolist()
    r=random.Random(seed)
    return [r.randint(1,x) for _ in range(n)]

def datasets(sizes=None,seed=0,x=MAXVALUE):
    if sizes is None:
        sizes=SIZES
    for n in sizes:
        yield n,generate(n,seed,x)

if __name__=="__main__":
    import time
    print("numpy available:",np is not None)
    print("value range: [1,",MAXVALUE,"]")
    print()
    print("     n        time     min       max     distinct   sample")
    for n in SIZES:
        t=time.perf_counter()
        a=generate(n)
        t=time.perf_counter()-t
        # a set of 10 million ints costs more memory than the array itself
        d=str(len(set(a))) if n<=1000000 else "-"
        print("%10d  %6.2fs  %6d  %8d  %11s   %s"%(n,t,min(a),max(a),d,a[:3]))
        del a

    print("\nsame seed gives the same array:",generate(1000,seed=7)==generate(1000,seed=7))
    print("different seed gives a different array:",generate(1000,seed=7)!=generate(1000,seed=8))
