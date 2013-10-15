from settings import *

def partition(participants, partitions, reliability):
    if sum(partitions) != participants:
        raise ValueError
    ptop = {}
    j = 0
    r = {}
    for i in range(participants):
        if partitions[0] == 0:
            j += 1
            partitions.pop(0)
        partitions[0] -= 1
        ptop[i] = j
    for i in range(participants):
        for j in range(participants):
            if i == j:
                continue
            if ptop[i] == ptop[j]:
                r[(i,j)] = 100
            else:
                r[(i,j)] = reliability
    return r

def reliability(x):
    return partition(CONFIG.PARTICIPANTS, CONFIG.PARTITIONS, x)
