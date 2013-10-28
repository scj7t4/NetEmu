import random
from protocol import SUC
from stats import *
from multitools import *
from settings import *


class Participant(object):
    def __init__(self,pid,premerge_v):
        self.AYC = False
        self.AYC_response = []
        self.remoteAYC = []
        self.invite = False
        self.invite_response = [] # replaces self.accept.
        self.remoteInvite = None
        self.ready = False
        self.remoteReady = False
        self.remoteInvite = None
        self.premerge_v = premerge_v
        self.acceptingRemoteInvite = True
        self.channels = {}
        self.pid = pid
    
        self.ayctimer = CONFIG.GLOBAL_TIMEOUT
        self.premerge = None
        self.peerwait = CONFIG.GLOBAL_TIMEOUT
        self.timeout = CONFIG.TIMEOUT_TIMEOUT
        self.ticks = 0

    def __repr__(self):
        return "AYC_R: {} / Inv: {} / R. Inv: {} / Rdy: {} / RmRdy: {}".format(self.AYC_response,
            self.invite, self.remoteInvite, self.ready, self.remoteReady)

    def add_channel(self, peer, channel):
        self.channels[peer] = channel
        
    def tick(self):
        self.ticks += 1    
    
        # If a premerge timer has been set and hasn't expired, tick the timer
        if self.premerge != None and self.premerge > 0 and self.remoteInvite == None:
            self.premerge -= 1
        
        #if you've sent and invite and you are the leader, and the timer for peers responding haven't expired, 
        if self.invite and not self.acceptingRemoteInvite and self.peerwait > 0:
            self.peerwait -= 1
            
        #if you've sent an AYC and and it hasn't expired, tick the timer
        if self.AYC and self.ayctimer > 0:
            self.ayctimer -= 1
            
        if len(self.AYC_response) > 0 and self.ayctimer == 0 and self.premerge == None:
            #If you've recieved a response and the timer has expired, select a premerge
            self.premerge = self.premerge_v
            
        #If you've recieved an invite but not the ready, tick down the timeout.
        if self.timeout > 0 and self.remoteInvite != None and self.acceptingRemoteInvite and not self.remoteReady:
            self.timeout -= 1

        if not self.AYC:
            for peer in self.channels:
                self.channels[peer].send("AYC")
            self.AYC = True

        if len(self.AYC_response) > 0 and self.ayctimer == 0 and self.premerge == 0 and self.remoteInvite == None and self.invite == False:
            #print "Setting {} as leader ({})".format(self.pid, self.ticks)
            for peer in self.channels:
                if peer in self.AYC_response:
                    self.channels[peer].send("INVITE")
            self.invite = True
            self.acceptingRemoteInvite = False

        if len(self.invite_response) > 0 and self.peerwait == 0 and not self.ready:
            for peer in self.channels:
                if peer in self.invite_response:
                    self.channels[peer].send("READY")
            self.ready = True
    
    def recv(self,peer,m):
        (t,s,msg) = m
        if msg == "AYC":
            self.remoteAYC.append(peer)
            self.channels[peer].send("AYC_R")

        elif msg == "AYC_R" and self.ayctimer > 0:
            self.AYC_response.append(peer)

        elif msg == "INVITE" and self.remoteInvite == None:
            #print "Inv from {} ({})".format(peer, self.ticks)
            if self.acceptingRemoteInvite == True:
                self.remoteInvite = peer
                self.channels[peer].send("ACCEPT")

        elif msg == "ACCEPT" and not self.acceptingRemoteInvite and self.peerwait > 0:
            self.invite_response.append(peer)

        elif msg == "READY" and self.timeout > 0 and self.remoteReady == False and self.remoteInvite == peer:
            self.remoteReady = True

    def aycfinished(self):
        if self.AYC and len(self.AYC_response) > 0:
            return True
        return False

    def finished(self):
        if self.ready or self.remoteReady:
            return True
        return False

def simulation(p):
    offsets = CONFIG.OFFSETS
    
    bad = 0
    quicks = 0
    slows = 0
    (r,q) = check(p,offsets)
    if r == True:
        return None
    elif len(q) == 0 or  max([len(g) for g in q]) <= 1:
        return [ (i,) for i in range(CONFIG.PARTICIPANTS) ]
    else:
        seen = set()
        for group in q:
            for peer in group:
                seen.add(peer)
        for i in range(CONFIG.PARTICIPANTS):
            if i not in seen:
                q.append( (i,) )   
        return q

def check(p, offsets):

    # The message channels (one for each pairing of nodes, (i,j)
    channels = {}
    peers = {}

    relmap = reliability(p)
    premerges = CONFIG.PREMERGES
    # For each pair of participiants, create a unidirectional channel and protocol between them.
    for i in range(CONFIG.PARTICIPANTS):
        peers[i] = Participant(i,premerges[i])
    
    for i in range(CONFIG.PARTICIPANTS):
        for j in range(CONFIG.PARTICIPANTS):
            if i == j:
                continue
            if i not in channels:
                channels[i] = {}
            channels[i][j] = CONFIG.PROTOCOL( relmap[ (i,j) ] ) 
            peers[i].add_channel(j, channels[i][j])

    # Attempt Counter
    s = 0
    # While the maximum number of attempts has not been reached and not all nodes are ready:
    while (s < CONFIG.ELECTION_MAX_TICKS+max(offsets)):
    
        # Advance each participants clock
        for peer in peers:
            if s >= offsets[peer]: 
                peers[peer].tick()
        
        # For each pair of nodes, see if any messages can be recieved
        mb = {}
        for i in range(CONFIG.PARTICIPANTS):
            for j in range(CONFIG.PARTICIPANTS):
                if i == j:
                    continue
                if (j,i) not in mb: # Message from i, to j.
                    mb[(j,i)] = []
                mb[(j,i)] = [ m for m in channels[i][j].tick() ]


        #for (k,v) in mb.iteritems():
        #    print "{} : {}".format(k,v)

        # For each pair of nodes, see if the recieved message is accepted by the protocol and delivered to j.
        for i in range(CONFIG.PARTICIPANTS):
            for j in range(CONFIG.PARTICIPANTS):
                if i == j:
                    continue
                for m in mb[(i,j)]:
                    if channels[i][j].recv(m):
                        peers[i].recv(j,m)

        # Mark an attempt.
        s += 1
    
    r = []
    for i in range(CONFIG.PARTICIPANTS):
        q = []
        if peers[i].invite == True and peers[i].finished():
            q.append(i)
            for j in range(CONFIG.PARTICIPANTS):
                if i == j:
                    continue
                #if j not in peers[i].invite_response:
                #    continue
                if peers[j].remoteInvite == i and peers[j].finished():
                    q.append(j)
            r.append(tuple(q))
    
    #print r
    """
    print r   

    for p in peers:
        print peers[p]
    """ 

    quick = True
    #evaluate if the failure mode is a slow failure or a fast one
    #A slow failure is when any communication channels get past the AYC phase
    #But fail to form a group.
    if any([ peers[peer].aycfinished() for peer in peers ]):
        quick = False    

    return (quick,r)

def main():
    CONFIG.print_profile_summary()
    resultset = {}
    for p in range(0,101,CONFIG.GRANULARITY):
        g = [ simulation(p) for i in range(CONFIG.ELECTION_TRIALS) ]
        # Sort them so that when you put them into a set (2,2,1) is the same as (1,2,2)
        qs = [ tuple(x) for x in g if x != None ]
        d = {}
        d['nocoordinators'] = sum([ 1 for x in g if x == None ])
        # d is a counting set
        for l in qs:
            try:
                d[str(l)] += 1
            except KeyError:
                d[str(l)] = 1
        #Print the failures
        resultset[p] = d
    print json.dumps(resultset, indent=4, sort_keys=True)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print "Give me an profile file as an argument and I will run that profile."
    else:
        CONFIG.load_from_profile(sys.argv[1])
        main() 
