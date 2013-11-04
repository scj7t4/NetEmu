import itertools

GROUPSIZE = 4

def generate():
    seen = set()
    for i in range(1,GROUPSIZE+1):
        counter = [ 0 for _ in range(i) ]
        while counter[-1] != GROUPSIZE:
            tmp = list(counter)
            dupe = set()
            valid = True
            for x in tmp:
                if x in dupe:
                    valid = False
                    break
                dupe.add(x)
            if valid:
                tmp = tuple(tmp[:1] + sorted(tmp[1:]))
                if tmp not in seen:
                    seen.add(tmp)
                    yield tmp
            for j in range(i):
                if counter[j] == GROUPSIZE-1 and j != i-1:
                    counter[j] = 0
                else:
                    counter[j] += 1
                    break


def combinedsize(l):
    c = 0
    for x in l:
        c += len(x)
    return c

def allunique(comb):
    s = set()
    for x in comb:
        for m in x:
            if m in s:
                return False
            s.add(m)
    return True    

def overviews():
    groups = [ g for g in generate() ]
    for i in range(1,GROUPSIZE+1):
        for comb in itertools.combinations(groups,i):
            if combinedsize(comb) == GROUPSIZE and allunique(comb):
                t = list(comb)
                t.sort()
                yield tuple(t)

def main():
    groups = []
    for x in generate():
        print x
        groups.append(x)
    for x in overviews():
        print x

if __name__ == "__main__":
    main()
