def MergeSort(arr: list) -> list:
    n = len(arr)

    if(n == 1):
        return arr

    arrA = arr[:int(n/2)]
    arrB = arr[int(n/2):]

    arrA = MergeSort(arrA)
    arrB = MergeSort(arrB)

    return Merge(arrA, arrB)

def Merge(arrA: list, arrB: list) -> list:
    aLen = len(arrA)
    bLen = len(arrB)

    arrC = []

    ai = bi = 0

    while(ai < aLen and bi < bLen):
        if(arrA[ai] < arrB[bi]):
            arrC.append(arrA[ai])
            ai += 1
        else:
            arrC.append(arrB[bi])
            bi += 1
    
    while(ai < aLen):
        arrC.append(arrA[ai])
        ai += 1

    while(bi < bLen):
        arrC.append(arrB[bi])
        bi += 1
    
    return arrC