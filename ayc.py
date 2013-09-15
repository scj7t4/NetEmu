import random
import protocol
import stats
from protocol import SUC,SRC


MAX_ATTEMPTS = 25
MAX_CHECKS = 32
TRIALS = 100

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
    while check(p,offset) and good < MAX_CHECKS:
        good += 1

    return good

def check(p, offset):
    leader = Participant()
    member = Participant()
    
    leader_p = SRC()
    member_p = SRC()

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
            if leader_p.recv(m):
                leader.recv(leader_p,m)
        for m in for_m:
            if member_p.recv(m):
                member.recv(member_p,m)

        s += 1

    #print leader
    #print member

    if leader.finished() and member.finished():
        return True
    return False

for p in range(0,101):
    g = [ simulation(p) for i in range(TRIALS) ]
    print "{}\t{}".format(p,"\t".join([str(x) for x in stats.stats_set(g)]))

