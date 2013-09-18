import random
import protocol
import stats
from protocol import SUC,SRC


MAX_ATTEMPTS = 50
MAX_CHECKS = 32
TRIALS = 50000
PARTICIPANTS = 10

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


def simulation(p):
    offset = 0
    while not protocol.attempt_delivery(p) and offset < MAX_ATTEMPTS:
        offset += 1
    
    good = 0
    v = PARTICIPANTS
    while v == PARTICIPANTS  and good < MAX_CHECKS:
        v = check(p,offset)
        good += 1

    return (v, good)

def check(p, offset):
    leader = [ (Participant(), SUC()) for x in range(PARTICIPANTS - 1) ]
    member = [ (Participant(), SUC()) for x in range(PARTICIPANTS - 1) ]
   
    s = 0
    while (s < MAX_ATTEMPTS and not all([ pr.finished() for (pr,_) in leader+member ]) ):
        for (par,pro) in leader:
            par.tick(pro)
        
        for (par,pro) in member:
            par.tick(pro)
        
        for_m = [ [ m for m in pr.tick(p) ] for (par, pr) in leader ]
        for_l = [ [ m for m in pr.tick(p) ] for (par, pr) in member ]

        #print for_m
        #print for_l

        for i in range(len(for_m)):
            for m in for_l[i]:
                if leader[i][1].recv(m):
                    leader[i][0].recv(leader[i][1],m)
        for i in range(len(for_l)):
            for m in for_m[i]:
                if member[i][1].recv(m):
                    member[i][0].recv(member[i][1],m)

        s += 1

    #print leader
    #print member

    return sum( [ 1 for i in range(PARTICIPANTS-1) if leader[i][0].finished() and member[i][0].finished() ] )+1

for p in range(0,101):
    c = [ simulation(p) for i in range(TRIALS) ]
    q = [ 0 for i in range(PARTICIPANTS+1) ]
    m = []
    for (v, good) in c:
        q[v] += 1
        m.append(good)
    print "{}\t{}\t{}".format(p,"\t".join([str(x) for x in stats.stats_set(m)]),"\t".join([str(x) for x in q]))

