import random
import protocol
from protocol import SUC,SRC
from multitools import *

class Participant(object):
    def __init__(self):
        self.AYQ = False
        self.AYQ_response = []
        self.AYQ_foreign = []
        self.channels = {}   

    def add_channel(self,peer,channel):
        self.channels[peer] = channel

    def tick(self):
        if not self.AYQ:
            for peer in self.channels:
                self.channels[peer].send("AYQ")
            self.AYQ = True

    def recv(self,peer,m):
        (t,s,msg) = m
        if msg == "AYQ" and peer not in self.AYQ_foreign:
            self.AYQ_foreign.append(peer)
            self.channels[peer].send("AYQ_R")
        elif msg == "AYQ_R" and peer not in self.AYQ_response:
            self.AYQ_response.append(peer)
    
    def finished(self):
        if self.AYQ and len(self.AYQ_response) > 0:
            return True
        return False

    def __repr__(self):
       return "{}\t{}\t{}".format(self.AYQ,self.AYQ_response,self.AYQ_foreign)


def simulation(p):
    offsets = CONFIG.OFFSETS
    
    good = 0
    v = CONFIG.PARTICIPANTS
    return check(p,offsets)


def check(p, offsets):
    leader = Participant()
    relmap = reliability(p)
    leader_channels = [ CONFIG.PROTOCOL(relmap[ (0,x+1) ]) for x in range(CONFIG.PARTICIPANTS - 1) ]
    c = 1
    for channel in leader_channels:
        leader.add_channel(c,channel)
        c += 1

    member = [ Participant() for x in range(CONFIG.PARTICIPANTS - 1) ]
    member_channels = [ CONFIG.PROTOCOL( relmap[ (x+1, 0) ]) for x in range(CONFIG.PARTICIPANTS - 1) ]
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

    group = [0]
    for peer in leader.AYQ_response:
        if 0 in member[peer-1].AYQ_response:
            group.append(peer)
    return tuple(sorted(group))

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
