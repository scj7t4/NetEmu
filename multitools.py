from settings import *

def partition(participants, partitions, reliability):
    if sum(partitions) != participants: 
        raise ValueError(str(partitions)+" "+str(participants))
    ptop = {}
    j = 0
    r = {}
    for i in range(participants):
        while len(partitions) > 0 and partitions[0] == 0:
            j += 1
            partitions.pop(0)
        if len(partitions) > 0:
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
    return partition(CONFIG.PARTICIPANTS, list(CONFIG.PARTITIONS), x)
