import random
from protocol import SUC

MAX_ATTEMPTS = 25
MAX_CHECKS = 32
TRIALS = 50000

"""
class SUC(object):
    def __init__(self):
        self.q = []
        self.ACK = None
        self.s = 0

    def tick(self,p):
        i = 0
        while i < len(self.q):
            if attempt_delivery(p):
                yield ('MSG',self.q[i][0],self.q[i][1])
                while i >= 0:
                    self.q.pop(0)
                    i -= 1
            i += 1
        if self.ACK and attempt_delivery(p):
            yield ('ACK',self.ACK,'')
            self.ACK = None

    def recv(self, msg):
        (t,s,m) = msg
        if t == 'ACK':
            while 0 < len(self.q) and self.q[0] <= s:
                self.q.pop(0)
        if t == 'MSG':
            self.ACK = s
            
    def send(self, msg):
        self.q.append((self.s,msg))
        self.s += 1
"""

class Participant(object):
    def __init__(self):
        self.AYQ = False
        self.AYQ_response = False
        self.AYQ_foreign = False
    
    def tick(self,protocol):
        if not self.AYQ:
            protocol.send("AYQ")
            self.AYQ = True
    
    def recv(self,protocol,m):
        (t,s,msg) = m
        if msg == "AYQ":
            self.AYQ_foreign = True
            protocol.send("AYQ_R")
        elif msg == "AYQ_R":
            self.AYQ_response = True
    
    def finished(self):
        if self.AYQ and self.AYQ_response and self.AYQ_foreign:
            return True
        return False

    def __repr__(self):
       return "{}\t{}\t{}".format(self.AYQ,self.AYQ_response,self.AYQ_foreign)

def attempt_delivery(p):
    if random.randint(1,100) <= p:
        return True
    return False
    

def simulation(p):
    offset = 0
    while not attempt_delivery(p) and offset < MAX_ATTEMPTS:
        offset += 1
    
    good = 0
    while check(p,offset) and good < MAX_CHECKS:
        good += 1

    return good

def check(p, offset):
    leader = Participant()
    member = Participant()
    
    leader_p = SUC()
    member_p = SUC()

    s = 0
    while (s < MAX_ATTEMPTS or (leader.finished() and s-offset < MAX_ATTEMPTS)) and (not leader.finished() or not member.finished()):
        leader.tick(leader_p)
        if s > offset:
            member.tick(member_p)
        
        for_m = [ m for m in leader_p.tick(p) ]
        for_l = [ m for m in member_p.tick(p) ]

        #print for_m
        #print for_l

        for m in for_l:
            leader_p.recv(m)
            leader.recv(leader_p,m)
        for m in for_m:
            member_p.recv(m)
            member.recv(member_p,m)

        s += 1

    #print leader
    #print member

    if leader.finished() and member.finished():
        return True
    return False

def avg(ds):
    return sum(ds)*1.0 / len(ds)

def median(ds):
    if len(ds) == 1:
        return ds[0]
    if len(ds) == 0:
        return None
    ds.sort()
    k = len(ds)/2
    q = len(ds)/2 % 1
    m = avg([ds[k], ds[k+q]])
    return m

def quartiles(ds):
    d = median(ds)
    q1 = median([ x for x in ds if x < d ])
    q3 = median([ x for x in ds if x >= d ])
    if q1 == None:
        q1 = d
    if q3 == None:
        q3 = d
    return [ min(ds), q1, d, q3, max(ds) ]

def stats_set(ds):
    a = avg(ds)
    variance = avg( [ (x - a)*(x - a) for x in ds ] )
    q = quartiles(ds)
    return [a,variance] + q

for p in range(0,101):
    g = [ simulation(p) for i in range(TRIALS) ]
    print "{}\t{}".format(p,"\t".join([str(x) for x in stats_set(g)]))

