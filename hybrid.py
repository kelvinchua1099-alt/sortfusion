# part (a): merge sort that switches to insertion sort once a subarray is <= S
# every function returns (sorted_list, key_comparisons)
# a key comparison is a comparison between two array elements,
# loop bounds like j>=0 and the size test len(arr)<=S are not counted

def merge(a,b):
    i=0
    j=0
    count=0
    new=[]
    while i<len(a) and j<len(b):
        count+=1
        if a[i]<=b[j]:
            new.append(a[i])
            i+=1
        else:
            new.append(b[j])
            j+=1
    if i<len(a):
        new.extend(a[i:])
    if j<len(b):
        new.extend(b[j:])
    return new,count

def insertsort(arr):
    arr=list(arr)
    count=0
    for i in range(1,len(arr)):
        key=arr[i]
        j=i-1
        while j>=0:
            count+=1
            if arr[j]>key:
                arr[j+1]=arr[j]
                j-=1
            else:
                break
        arr[j+1]=key
    return arr,count

def mergesort(arr):
    if len(arr)<2:
        return list(arr),0
    mid=len(arr)//2
    left,c1=mergesort(arr[:mid])
    right,c2=mergesort(arr[mid:])
    new,c3=merge(left,right)
    return new,c1+c2+c3

def hybrid(arr,S):
    if S<1:
        raise ValueError("S must be at least 1")
    if len(arr)<=S:
        return insertsort(arr)
    mid=len(arr)//2
    left,c1=hybrid(arr[:mid],S)
    right,c2=hybrid(arr[mid:],S)
    new,c3=merge(left,right)
    return new,c1+c2+c3

if __name__=="__main__":
    import random
    random.seed(20260906)

    print("correctness")
    for n in [0,1,2,3,17,100,1000,4096]:
        data=[random.randint(1,1000) for _ in range(n)]
        want=sorted(data)
        ok_i=insertsort(data)[0]==want
        ok_m=mergesort(data)[0]==want
        ok_h=all(hybrid(data,S)[0]==want for S in [1,2,5,16,64,n+5])
        print("  n=",n," insert=",ok_i," merge=",ok_m," hybrid=",ok_h)

    print("\nS=1 should match plain merge sort exactly")
    for n in [10,100,1000,5000]:
        data=[random.randint(1,10000) for _ in range(n)]
        cm=mergesort(data)[1]
        ch=hybrid(data,1)[1]
        print("  n=",n," merge=",cm," hybrid(S=1)=",ch," same=",cm==ch)

    print("\ninsertion sort should be adaptive now")
    print("  sorted   n=1000 ->",insertsort(list(range(1,1001)))[1],"(expect 999)")
    print("  reversed n=1000 ->",insertsort(list(range(1000,0,-1)))[1],"(expect 499500)")

    print("\nkey comparisons over S, n=100000")
    data=[random.randint(1,10000000) for _ in range(100000)]
    for S in [1,2,4,8,16,32,64,128,256]:
        print("  S=",S," ->",hybrid(data,S)[1])
