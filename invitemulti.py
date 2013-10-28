import random
import protocol
import stats
from protocol import SUC,SRC
from multitools import *

class Participant(object):
    def __init__(self,leader):
        self.leader = leader
        self.remoteinvite = None
        self.invite = False
        self.accept = []
        self.ready_sent = False
        self.ready = []
        self.channels = {}
        self.response_timeout = CONFIG.GLOBAL_TIMEOUT 
        self.ready_timeout = CONFIG.TIMEOUT_TIMEOUT

    def add_channel(self,peer,channel):
        self.channels[peer] = channel

    def tick(self):
        if self.invite == True and self.response_timeout > 0:
            self.response_timeout -= 1
        if self.remoteinvite != None and self.ready_timeout > 0:
            self.ready_timeout -= 1
        if self.invite == False and self.leader == True:
            for peer in self.channels:
                self.channels[peer].send("Invite")
            self.invite = True
        if self.response_timeout == 0:
            for peer in self.accept:
                self.channels[peer].send("Ready")

    def recv(self,peer,m):
        (t,s,msg) = m
        if msg == "Invite" and self.remoteinvite == None:
            self.remoteinvite = peer
            self.channels[peer].send("Accept")
        elif msg == "Accept" and peer not in self.accept and self.response_timeout > 0:
            self.accept.append(peer)
        elif msg == "Ready" and peer not in self.ready and self.ready_timeout > 0:
            self.ready.append(peer)

    def finished(self):
        if len(self.ready) > 0 or self.ready_sent:
            return True
        return False


def simulation(p):
    offsets = CONFIG.OFFSETS
    
    good = 0
    v = CONFIG.PARTICIPANTS
    return check(p,offsets)

def check(p, offsets):
    leader = Participant(True)
    leader_channels = [ CONFIG.PROTOCOL(p) for x in range(CONFIG.PARTICIPANTS - 1) ]
    c = 1
    for channel in leader_channels:
        leader.add_channel(c,channel)
        c += 1

    member = [ Participant(False) for x in range(CONFIG.PARTICIPANTS - 1) ]
    member_channels = [ CONFIG.PROTOCOL(p) for x in range(CONFIG.PARTICIPANTS - 1) ]
    for party, channel in zip(member,member_channels):
        party.add_channel(0,channel)
   

    s = 0
    while (s < CONFIG.AYC_MAX_TICKS+max(offsets) and not all([ pr.finished() for pr in [leader]+member ]) ):
        if s >= offsets[0]:
            leader.tick()    
    
        for i in range(len(member)):
            par = member[i]
            if s >= offsets[i+1]:
                par.tick()
        
        for_m = [ [ m for m in pr.tick() ] for pr in leader_channels ]
        for_l = [ [ m for m in pr.tick() ] for pr in member_channels ]

        #print for_m
        #print for_l

        for i in range(len(for_m)):
            for m in for_l[i]:
                if leader_channels[i].recv(m):
                    leader.recv(i+1,m)
        for i in range(len(for_l)):
            for m in for_m[i]:
                if member_channels[i].recv(m):
                    member[i].recv(0,m)

        s += 1

    #print leader
    #print member

    return sum([ 1 for m in member if m.finished()])


def main():
    CONFIG.print_profile_summary()
    rset = {}
    for p in range(0,101,CONFIG.GRANULARITY):
        c = [ simulation(p) for i in range(CONFIG.AYC_TRIALS) ]
        d = {}
        for i in c:
            try:
                d[ str(i) ] += 1
            except KeyError:
                d[ str(i) ] = 1
        rset[p] = d
    print json.dumps(rset, indent=4, sort_keys=True)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print "Give me an profile file as an argument and I will run that profile."
    else:
        CONFIG.load_from_profile(sys.argv[1])
        main() 
