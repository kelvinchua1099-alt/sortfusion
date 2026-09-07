# where the time actually goes on a small subarray.
# section 5 of the report cites these numbers.
# do not run this while anything else is loading the machine.

import random
import time
import statistics
from hybrid import insertsort_nc,mergesort_nc

M=8
POOL=4000

def counts(m,seed=3):
    calls=slices=leafcopy=mergecalls=appends=extends=newlists=0
    def ms(arr):
        nonlocal calls,slices,leafcopy,mergecalls,newlists,appends,extends
        calls+=1
        if len(arr)<2:
            leafcopy+=1
            return list(arr)
        mid=len(arr)//2
        slices+=2
        left=ms(arr[:mid]); right=ms(arr[mid:])
        mergecalls+=1; newlists+=1
        i=j=0; new=[]
        while i<len(left) and j<len(right):
            if left[i]<=right[j]: new.append(left[i]); i+=1
            else: new.append(right[j]); j+=1
            appends+=1
        if i<len(left): new.extend(left[i:]); extends+=1; slices+=1
        if j<len(right): new.extend(right[j:]); extends+=1; slices+=1
        return new
    r=random.Random(seed)
    ms([r.randint(1,10**7) for _ in range(m)])
    return dict(calls=calls,merges=mergecalls,slices=slices,leafcopy=leafcopy,
                newlists=newlists,appends=appends,extends=extends)

# merge sort with its layers peeled off, so each layer's cost can be isolated
def skeleton(arr):
    if len(arr)<2: return list(arr)
    mid=len(arr)//2
    left=skeleton(arr[:mid]); right=skeleton(arr[mid:])
    return left

def nomerge(arr):
    if len(arr)<2: return list(arr)
    mid=len(arr)//2
    left=nomerge(arr[:mid]); right=nomerge(arr[mid:])
    new=[]; new.extend(left); new.extend(right)
    return new

def bench(fn,pool,reps=7):
    best=None
    for _ in range(reps):
        t=time.process_time()
        for a in pool: fn(a)
        dt=time.process_time()-t
        if best is None or dt<best: best=dt
    return best/len(pool)*1e6

if __name__=="__main__":
    c=counts(M)
    print("one merge sort of an array of %d elements performs"%M)
    print("  %3d  mergesort() calls, of which %d are on a single element"%(c["calls"],(M)))
    print("  %3d  merge() steps"%c["merges"])
    print("  %3d  list slices"%c["slices"])
    print("  %3d  list() copies at the leaves"%c["leafcopy"])
    print("  %3d  new result lists"%c["newlists"])
    print("  %3d  appends, %d extends"%(c["appends"],c["extends"]))
    print("  ~16  key comparisons\n")
    print("one insertion sort of the same array performs")
    print("    1  call, 1 list() copy, 0 slices, 0 new lists")
    print("  ~19  key comparisons, ~19 in-place assignments\n")

    random.seed(4)
    pool=[[random.randint(1,10**7) for _ in range(M)] for _ in range(POOL)]
    sk=bench(skeleton,pool); nm=bench(nomerge,pool)
    pm=bench(mergesort_nc,pool); pi=bench(insertsort_nc,pool)
    print("microseconds per sort, best of 7 x %d"%POOL)
    print("  recursion + slices + leaf copies only          %6.3f"%sk)
    print("  + allocating the result lists                  %6.3f  (+%.3f)"%(nm,nm-sk))
    print("  + the merging itself                           %6.3f  (+%.3f)"%(pm,pm-nm))
    print("  " + "-"*47)
    print("  full merge sort                                %6.3f"%pm)
    print("  insertion sort                                 %6.3f"%pi)
    print("  saved by switching at m=%d                      %6.3f"%(M,pm-pi))
    print()
    print("  scaffolding as a share of merge sort           %5.1f%%"%(100*nm/pm))
    print("  merging step alone vs whole insertion sort     %.2fx"%((pm-nm)/pi))
