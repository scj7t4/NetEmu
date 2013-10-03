import random
from protocol import SUC
from stats import *
from multitools import *

# 5 seconds for AYC
# 30 for premerge
# 5 for accepts
# 5 for readys
# 45 seconds total
# 225 @ 200ms, 450 @ 100ms
GLOBAL_TIMEOUT = 50
TIMEOUT_TIMEOUT = 100
CHECK_TIMEOUT = 100

PREMERGE_MIN = 50
PREMERGE_MAX = 150 

MAX_ATTEMPTS = 500
MAX_CHECKS = 50
TRIALS = 10

class Participant(object):
    def __init__(self,premerge_v=None):
        self.AYC = False
        self.AYC_response = []
        self.remoteAYC = []
        self.invite = False
		self.invite_response = [] # replaces self.accept.
        self.remoteInvite = None
        self.ready = False
        self.remoteReady = None
        self.remoteInvite = False
        self.premerge_v = random.randint(50,150) if premerge_v == None else premerge_v
		self.acceptingRemoteInvite = True
		self.channels = {}
	
        self.ayctimer = GLOBAL_TIMEOUT
        self.premerge = None
        self.peerwait = GLOBAL_TIMEOUT
        self.timeout = TIMEOUT_TIMEOUT
        self.ticks = 0

	def add_channel(self, peer, channel):
		self.channels[peer] = channel
		
    def tick(self):
        #if you've sent and invite and you are the leader, and the timer for peers responding haven't expired, tick
        if self.invite and not self.acceptingRemoteInvite and self.peerwait > 0:
            self.peerwait -= 1
			
        #if you've sent an AYC and and it hasn't expired, tick the timer
        if self.AYC and self.ayctimer > 0:
            self.ayctimer -= 1
			
		# If a premerge timer has been set and hasn't expired, tick the timer
		if self.premerge != None and self.premerge > 0 and not self.remoteInvite:
            self.premerge -= 1
			
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

        if len(self.AYC_response) > 0 and self.ayctimer == 0 and self.premerge == 0 and not self.remoteInvite and not self.invite:
			for peer in self.channels:
				if peer in self.AYC_response:
					protocol.send("INVITE")
            self.invite = True
            self.acceptingRemoteInvite = False

        if self.peerwait == 0 and not self.ready:
			for peer in self.channels:
				if peer in self.invite_response:
					protocol.send("READY")
            self.ready = True
    
    def recv(self,peer,m):
        (t,s,msg) = m
        if msg == "AYC":
            self.remote_AYC.append(peer)
            self.channels[peer].send("AYC_R")

        elif msg == "AYC_R" and self.ayctimer > 0:
            self.AYC_response.append(peer)

        elif msg == "INVITE" and self.remoteInvite == None:
            if self.acceptingRemoteInvite == True:
				self.remoteInvite = peer
                self.channels[peer].send("ACCEPT")

        elif msg == "ACCEPT" and not self.acceptingRemoteInvite and self.peerwait > 0:
			self.invite_response.append(peer)

        elif msg == "READY" and self.timeout > 0 and self.remoteReady == None and self.remoteInvite == peer:
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

    # The message channels (one for each pairing of nodes, (i,j)
    channels = {}
	peers = {}

    relmap = reliability(p)
    # For each pair of participiants, create a unidirectional channel and protocol between them.
	for i in range(PARTICIPANTS):
		peer[i] = Participant()
	
    for i in range(PARTICIPANTS):
        for j in range(PARTICIPANTS):
            if i == j:
                continue
            if i not in channels:
                channels[i] = {}
            channels[i][j] = SUC(relmap[(i,j)]) 
			peer[i].add_channel(j, channels[i][j])

    # Attempt Counter
    s = 0
    # While the maximum number of attempts has not been reached and not all nodes are ready:
    while (s < MAX_ATTEMPTS and ( not all([peer.finished() for peer in peers]) ) ):
	
        # Advance each participants clock
        for peer in peers:
			peers[peer].tick()
        
        # For each pair of nodes, see if any messages can be recieved
        mb = {}
        for i in range(PARTICIPANTS):
			for j in range(PARTICIPANTS):
				if i == j:
					continue:
				if (j,i) not in mb: # Message from i, to j.
					mb[(j,i)] = []
				mb[(j,i)] += [ m for m in channels[i][j].tick() ]


        #for (k,v) in mb.iteritems():
        #    print "{} : {}".format(k,v)

        # For each pair of nodes, see if the recieved message is accepted by the protocol and delivered to j.
        for i in range(PARTICIPANTS):
			for j in range(PARTICIPANTS):
				if i == j:
					continue:
				for m in mb[(j,i)]:
					if channel[j][i].recv(m):
						peer[j].recv(i,m)

        # Mark an attempt.
        s += 1
    
    r = []
    for i in range(PARTICIPANTS):
        q = []
        if peer[i].invite == True:
            q.append(i)
            for j in range(PARTICIPANTS):
                if i == j:
                    continue
				if peer[j].remoteInvite == i and peer[j].remoteReady == True:
					q.append(j)
            r.append(tuple(q))
    
    quick = True
    #evaluate if the failure mode is a slow failure or a fast one
    #A slow failure is when all communication channels get past the AYC phase
    #But fail to form a group.
    if any([ peer.aycfinished() for peer in peers ]):
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
