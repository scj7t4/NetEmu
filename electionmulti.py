import random
from protocol import SUC
from stats import *

MAX_ATTEMPTS = 200
MAX_CHECKS = 50
TRIALS = 500
PARTICIPANTS = 10


"""
for i in range(0,101):
    s = 0.0
    t = 50000
    for j in range(t):
        s += 1 if attempt_delivery(i) else 0
"""

class CommonStore(object):
    def __init__(self,premerge_v=None):
        self.invite = False
        self.accept = False
        self.invite_foreign = False
        self.ready_foreign = False
        self.leader = False
        self.premerge_v = random.randint(0,100) if premerge_v == None else premerge_v
        self.ayctimer = 25
        self.premerge = None
        self.peerwait = 25
        self.timeout = 50
        self.ticks = 0
        self.enable_premerge = False
        self.ready = False
        self.enable_ayctimer = False

    def tick(self):
        # If a premerge timer has been set and hasn't expired, tick the timer
        if self.premerge != None and self.premerge > 0 and not self.invite_foreign:
            self.premerge -= 1
        #if you've sent and invite and you are the leader, and the timer for peers responding haven't expired, tick
        if self.invite and self.leader and self.peerwait > 0:
            self.peerwait -= 1
        #if you've sent an AYC and and it hasn't expired, tick the timer
        if self.enable_ayctimer and self.ayctimer > 0:
            self.ayctimer -= 1
        if self.enable_premerge and self.ayctimer == 0 and self.premerge == None:
            #If you've recieved a response and the timer has expired, select a premerge
            self.premerge = self.premerge_v
        #If you've recieved an invite but not the ready, tick down the timeout.
        if self.timeout > 0 and self.invite_foreign and not self.leader and not self.ready_foreign:
            self.timeout -= 1

    def finished(self):
        if self.ready or self.ready_foreign:
            return True
        return False


class Participant(object):
    def __init__(self,common):
        self.AYC = False
        self.AYC_response = False
        self.AYC_foreign = False
        self.ready = False
        self.accept_foreign = False
        self.sent_invite = False
        self.invite_from_this = False
        self.common = common 

    def tick(self,protocol):
        if self.AYC_response and self.common.enable_premerge == False:
            #If you've recieved a response and the timer has expired, select a premerge
            self.common.enable_premerge = True

        if not self.AYC:
            protocol.send("AYC")
            self.AYC = True
            self.common.enable_ayctimer = True

        if self.AYC_response and self.common.ayctimer == 0 and self.common.premerge == 0 and not self.common.invite_foreign:
            self.common.leader = True

        if self.common.leader and not self.sent_invite:
            protocol.send("INVITE")
            self.common.invite = True
            self.sent_invite = True

        if self.accept_foreign and self.common.peerwait == 0 and not self.ready:
            protocol.send("READY")
            self.common.ready = True
            self.ready = True   
 
    def recv(self,protocol,m):
        (t,s,msg) = m
        if msg == "AYC":
            self.AYC_foreign = True
            protocol.send("AYC_R")

        elif msg == "AYC_R" and self.common.ayctimer > 0:
            self.AYC_response = True

        elif msg == "INVITE" and not self.common.invite_foreign:
            self.common.invite_foreign = True
            self.invite_from_this = True
            if self.common.leader == False:
                protocol.send("ACCEPT")

        elif msg == "ACCEPT" and self.common.leader and self.common.peerwait > 0:
            self.accept_foreign = True

        elif msg == "READY" and self.common.timeout > 0 and not self.common.ready_foreign and self.invite_from_this == True:
            self.common.ready_foreign = True

    def aycfinished(self):
        if self.AYC and self.AYC_response:
            return True
        return False



def simulation(p):
    offset = 50
    
    bad = 0
    quicks = 0
    slows = 0
    while bad < MAX_CHECKS:
        (r,q) = check(p,offset)
        if r == True:
            quicks += 1
        else:
            if max(q) == 1:
                #print q
                slows += 1
            else:
                break
        bad += 1

    return (quicks, slows, q)

def check(p, offset):
    # The values stored globably by each processes (Shared betweeen all channels)
    commons = [ CommonStore() for c in range(PARTICIPANTS) ]
    # A helper for the iterators
    iterthing = []
    # The message channels (one for each pairing of nodes, (i,j)
    channel = {}

    # For each pair of participiants, create a unidirectional channel and protocol between them.
    for i in range(PARTICIPANTS):
        for j in range(PARTICIPANTS):
            if i == j:
                continue
            iterthing.append( (i,j) )
            if i not in channel:
                channel[i] = {}
            channel[i][j] = ( Participant(commons[i]), SUC() )

    # Attempt Counter
    s = 0
    # While the maximum number of attempts has not been reached and not all nodes are ready:
    while (s < MAX_ATTEMPTS and ( not all([c.ready for c in commons]) ) ):

        for c in commons:
            c.tick()

        # Advance each participants clock
        for (i,j) in iterthing:
            channel[i][j][0].tick(channel[i][j][1])
        
        # For each pair of nodes, see if any messages can be recieved
        mb = {}
        for (i,j) in iterthing:
            if (j,i) not in mb:
                mb[(j,i)] = []
            mb[(j,i)] += [ m for m in channel[i][j][1].tick(p) ]


        #for (k,v) in mb.iteritems():
        #    print "{} : {}".format(k,v)

        # For each pair of nodes, see if the recieved message is accepted by the protocol and delivered to j.
        for (i,j) in iterthing:
            for m in mb[(i,j)]:
                if channel[i][j][1].recv(m):
                    channel[i][j][0].recv(channel[i][j][1],m)

        # Mark an attempt.
        s += 1
    
    r = []
    for i in range(PARTICIPANTS):
        if commons[i].leader == True:
            d = 1
            for j in range(PARTICIPANTS):
                if i == j:
                    continue
                if channel[j][i][0].invite_from_this and channel[j][i][0].common.finished():
                    d += 1
            r.append(d)
    
    quick = True
    #evaluate if the failure mode is a slow failure or a fast one
    #A slow failure is when all communication channels get past the AYC phase
    #But fail to form a group.
    if any([ channel[i][j][0].aycfinished() for (i,j) in iterthing ]):
        quick = False    
    
 
    return (quick,r)

for p in range(0,100):
    g = [ simulation(p) for i in range(TRIALS) ]
    # Collect the quick failures
    g1 = [ x[0] for x in g ]
    # Collect the slow failures
    g2 = [ x[1] for x in g ]
    # Collect the groups that are formed
    qs = [ x[2] for x in g ]
    # Sort them so that when you put them into a set (2,2,1) is the same as (1,2,2)
    qs = [ tuple(sorted(x)) for x in qs ]
    # d is a counting set
    d = {}
    for l in qs:
        try:
            d[l] += 1
        except KeyError:
            d[l] = 1
    #Print the failures
    print "{}\tQUICKS\t{}\tSLOWS\t{}".format(p,
        "\t".join([str(x) for x in stats_set(g1)]),
        "\t".join([str(x) for x in stats_set(g2)]),
        )
    #Print the counts of the different types of groups formed;
    for (k,v) in d.iteritems():
        print "#{}: {}".format(k,v)

