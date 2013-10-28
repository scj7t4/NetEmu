from protocol import attempt_delivery

def evaluator(offsets):
    TRIALS = 50000
    for p in range(1,101):
        goods = 0
        q = []
        for _ in range(TRIALS):
            a = False
            b = False
            c = 0
            while a == False and b == False:
                a = attempt_delivery(p)
                if offsets == None or c >= offsets[p]:
                    b = attempt_delivery(p)
                c += 1
            if a == True:
                goods += 1
            q.append(c)
        r = ((TRIALS-goods) * 1.0) / TRIALS
        d = sum(q)*1.0 / TRIALS
        print "{}\t{}\t{}".format(p,r,d)
        yield p,d 

offsets = None
for _ in range(20):
    r = [ x for x in evaluator(offsets) ]
    offsets = {}
    for (k,v) in r:
        offsets[k] = v
