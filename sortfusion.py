# the default is in a rising sequence
import random
def merge(a,b):
    i=0
    j=0
    new=[]
    while i<len(a) and j<len(b):
        if a[i]<b[j]:
            new.append(a[i])
            i+=1
        else:
            new.append(b[j])
            j+=1
    if i<len(a):
        new.extend(a[i:])
    if j<len(b):
        new.extend(b[j:])
    return new
def split(arr):
    length=len(arr)
    mid = length // 2
    left = arr[:mid]
    right = arr[mid:]
    left=arr[:mid]
    right=arr[mid:]
    left_arranged=1
    right_arranged=1
    if len(left)!=1:
        for i in range(len(left)-1):
            if left[i+1]<left[i]:
                left_arranged=0
    if len(right)!=1:
        for i in range(len(right)-1):
            if right[i+1]<right[i]:
                right_arranged=0
    if left_arranged and right_arranged:
        return merge(left,right)
    elif left_arranged:
        return merge(left,split(right))
    elif right_arranged:
        return merge(split(left),right)
    else:
        return merge(split(left),split(right))
def split_v2(arr):
    length=len(arr)
    mid = length // 2
    left = arr[:mid]
    right = arr[mid:]
    left=arr[:mid]
    right=arr[mid:]
    left_arranged=1
    right_arranged=1
    if len(left)!=1:
        for i in range(len(left)-1):
            if left[i+1]<left[i]:
                left_arranged=0
    if len(right)!=1:
        for i in range(len(right)-1):
            if right[i+1]<right[i]:
                right_arranged=0
    if left_arranged and right_arranged:
        return 2
    elif left_arranged:
        return 1+split_v2(right)
    elif right_arranged:
        return 1+split_v2(left)
    else:
        return split_v2(left)+split_v2(right)
def mergesort(arr):
    return split(arr)
def insertsort(arr):
    length=len(arr)
    for i in range(length):
        for j in range(i,0,-1):
            if arr[j-1]>arr[j]:
                p=arr[j]
                arr[j]=arr[j-1]
                arr[j-1]=p
    return arr
def hybrid_sort(arr,S):
    if split_v2(arr)>S:
        return insertsort(arr)
    else:
        return mergesort(arr)
if __name__ == "__main__":
    size=10000
    sample_array=[random.randint(0,1000) for _ in range(size)]
    s=int(input("what's the threshold?"))
    organized_arr=insertsort(sample_array)
    merge_arr=mergesort(sample_array)
    hybrid_arr=hybrid_sort(sample_array,s)
    print(organized_arr==merge_arr)
    print(hybrid_arr==organized_arr)
    
    
           
                
    
    