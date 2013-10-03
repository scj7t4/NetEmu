import random
from protocol import SUC
from stats import *

# 5 seconds for AYC
# 30 for premerge
# 5 for accepts
# 5 for readys
# 45 seconds total
# 225 @ 200ms, 450 @ 100ms
MAX_ATTEMPTS = 225
MAX_CHECKS = 50
TRIALS = 5000


"""
for i in range(0,101):
    s = 0.0
    t = 50000
    for j in range(t):
        s += 1 if attempt_delivery(i) else 0
    print "{}: {}".format(i,s/t)
"""

class Participant(object):
    def __init__(self,premerge_v=None):
        self.AYC = False
        self.AYC_response = False
        self.AYC_foreign = False
        self.invite = False
        self.accept = False
        self.invite_foreign = False
        self.ready = False
        self.ready_foreign = False
        self.accept_foreign = False
        self.leader = False
        self.premerge_v = random.randint(50,150) if premerge_v == None else premerge_v
    
        self.ayctimer = 25
        self.premerge = None
        self.peerwait = 25
        self.timeout = 50
        self.ticks = 0

    def tick(self,protocol):
        # If a premerge timer has been set and hasn't expired, tick the timer
        if self.premerge != None and self.premerge > 0 and not self.invite_foreign:
            self.premerge -= 1
        #if you've sent and invite and you are the leader, and the timer for peers responding haven't expired, tick
        if self.invite and self.leader and self.peerwait > 0:
            self.peerwait -= 1
        #if you've sent an AYC and and it hasn't expired, tick the timer
        if self.AYC and self.ayctimer > 0:
            self.ayctimer -= 1
        if self.AYC_response and self.ayctimer == 0 and self.premerge == None:
            #If you've recieved a response and the timer has expired, select a premerge
            self.premerge = self.premerge_v
        #If you've recieved an invite but not the ready, tick down the timeout.
        if self.timeout > 0 and self.invite_foreign and not self.leader and not self.ready_foreign:
            self.timeout -= 1

        if not self.AYC:
            protocol.send("AYC")
            self.AYC = True

        if self.AYC_response and self.ayctimer == 0 and self.premerge == 0 and not self.invite_foreign and not self.invite:
            protocol.send("INVITE")
            self.invite = True
            self.leader = True

        if self.accept_foreign and self.peerwait == 0 and not self.ready:
            protocol.send("READY")
            self.ready = True
    
    def recv(self,protocol,m):
        (t,s,msg) = m
        if msg == "AYC":
            self.AYC_foreign = True
            protocol.send("AYC_R")

        elif msg == "AYC_R" and self.ayctimer > 0:
            self.AYC_response = True

        elif msg == "INVITE" and not self.invite_foreign:
            self.invite_foreign = True
            if self.leader == False:
                protocol.send("ACCEPT")

        elif msg == "ACCEPT" and self.leader and self.peerwait > 0:
            self.accept_foreign = True

        elif msg == "READY" and self.timeout > 0 and not self.ready_foreign:
            self.ready_foreign = True

    def aycfinished(self):
        if self.AYC and self.AYC_response:
            return True
        return False

    def finished(self):
        if self.ready or self.ready_foreign:
            return True
        return False


def simulation(p):
    offset = 50
    
    bad = 0
    quicks = 0
    slows = 0
    while bad < MAX_CHECKS:
        r = check(p,offset)
        if r == 0:
            quicks += 1
        elif r == 1:
            slows += 1
        else:
            break
        bad += 1

    return (quicks, slows)

def check(p, offset):
    leader = Participant(100)
    member = Participant(50)
    
    leader_p = SUC()
    member_p = SUC()

    s = 0
    while (s < MAX_ATTEMPTS and (not leader.finished() or not member.finished()) ):
        leader.tick(leader_p)
        if s > offset:
            member.tick(member_p)
        
        for_m = [ m for m in leader_p.tick(p) ]
        for_l = [ m for m in member_p.tick(p) ]

        #print "To Member ",for_m
        #print "To Leader ",for_l

        for m in for_l:
            leader_p.recv(m)
            leader.recv(leader_p,m)
        for m in for_m:
            member_p.recv(m)
            member.recv(member_p,m)

        s += 1
    
    if leader.finished() and member.finished():
        return 2
    if leader.aycfinished() or member.aycfinished():
        return 1
    return 0

for p in range(0,100):
    g = [ simulation(p) for i in range(TRIALS) ]
    g1 = [ x[0] for x in g ]
    g2 = [ x[1] for x in g ]
    print "{}\tQUICKS\t{}\tSLOWS\t{}".format(p,
        "\t".join([str(x) for x in stats_set(g1)]),
        "\t".join([str(x) for x in stats_set(g2)]),
        )

