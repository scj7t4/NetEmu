import itertools
import json
import subprocess
import groupgen

AYT_RATE = 5
ELECTION_DURATION = 15
PARTICIPANTS = 4

def loadmapping(filename):
    f = open(filename)
    trans = {}
    for line in f:
        if line.find("#") != -1:
            #print "Comment: {}".format(line)
            continue
        tokens = line.split('\t')
        if len(tokens) < 3:
            #print "Saw {} tokens for {}".format(len(tokens),line)
            continue
        group = eval(tokens[0])
        trans[ group ] = {}
        trans[ group ]['conf'] = tokens[1]
        trans[ group ]['map'] = eval( tokens[2] )
    f.close()
    return trans

def applymapping(group, mapping):
    r = []
    for m in group:
        r.append(mapping[m])
    r = r[:1] + sorted(r[1:])
    return tuple(r)
    
def loadtransitionfile(type,config):
    if config == None or config == "None":
        return {}
    fname = "out/{}-{}.dat".format(type,config)
    fp = open(fname)
    result = ""
    for line in fp:
        if line.find("##") == -1:
            result += line
    #print result
    if len(result) > 0:
        d1 = json.loads(result)
    else:
        return {}
    d2 = {}
    for k1 in d1:
        d2[k1] = {}
        for k2 in d1[k1]:
            if k2 != "nocoordinators":
                d2[k1][ eval(k2) ] = d1[k1][k2]
            else:
                d2[k1][k2] = d1[k1][k2]
    return d2
    
def remaptransitions(mapping, transitions):
    r = {}
    for k in transitions:
        r[k] = applymapping(transitions[k], mapping)
    return r
    
def make_state(config):
    seen = set()
    config = [ g.members for g in config ]
    for g in config:
        for m in g:
            seen.add(m)
    for i in range(PARTICIPANTS):
        if i not in seen:
            config.append( (i,) )
    config.sort()
    return StatePool.getsystembytuple( tuple(config) )
    
    
class Group(object):
    members = None
    def __init__(self,gtuple):
        self.members = gtuple
        d = loadmapping('AYT-trans.tsv')
        config =  d[ self.members ]['conf']
        peermap = d[ self.members ]['map']
        tjson = loadtransitionfile('AYC',config)
        self.transitions = {}
        self.nochange = {}
        self.transaway = {}
        for reliability, possibilites in tjson.iteritems():
            reliability = int(reliability)
            self.transitions[reliability] = {}
            self.nochange[reliability] = 0
            self.transaway[reliability] = 0
            for possibility,transitions in possibilites.iteritems():
                remapped = applymapping(possibility, peermap)
                if remapped == self.members:
                    self.nochange[reliability] += transitions
                    continue
                self.transaway[reliability] += transitions
                self.transitions[reliability][ remapped ] = transitions
                
    def getnochange(self,probability):
        return self.nochange[probability]
    
    def gettransitions(self,probability):
        if probability in self.transitions:
            for group,transitions in self.transitions[probability].iteritems():
                if group != self.members:
                    yield ( StatePool.getgroupbytuple(group),  transitions*1.0 / self.transaway[probability] )
            
    def getlambda(self,probability):
        try:  
            total = self.nochange[probability] + self.transaway[probability]
            successrate = (self.nochange[probability] * 1.0) / total
            print successrate
        except KeyError:
            return 0.0
        try:
            return (1 - successrate) / AYT_RATE
        except ZeroDivisionError:
            return float("inf")
    
    def __repr__(self):
        return str(self.members)
        
    def __eq__(self,other):
        return self.members == other.members
        
    def __ne__(self,other):
        return self.members != other.members
    
    def __hash__(self):
        return self.members.__hash__()
        
    
class StatePool(object):
    gpool = {}
    spool = {}
    
    @staticmethod
    def getgroupbytuple(gtuple):
        if gtuple not in StatePool.gpool:
            StatePool.gpool[gtuple] = Group(gtuple)
        return StatePool.gpool[gtuple]
        
    @staticmethod
    def getsystembytuple(stuple):
        stuple = tuple(sorted(list(stuple)))
        if stuple not in StatePool.spool:
            StatePool.spool[stuple] = SystemConfig(stuple)
        return StatePool.spool[stuple]        
        
class SystemConfig(object):
    config = None
    def __init__(self, stuple):
        config = []
        stuple = tuple(sorted(list(stuple)))
        for group in stuple:
            config.append( StatePool.getgroupbytuple(group) )
        config.sort(key=lambda x: x.members)
        self.config = tuple(config)
        d = loadmapping('ELECTION-trans.tsv')
        config = d[ stuple ]['conf']
        peermap = d[ stuple ]['map']
        #print config
        #print peermap
        tjson = loadtransitionfile('ELECTION',config)
        #print tjson
        self.transitions = {}
        self.nochange = {}
        self.transaway = {}
        for reliability, possibilities in tjson.iteritems():
            reliability = int(reliability)
            print reliability
            self.transitions[reliability] = {}
            self.transaway[reliability] = 0
            self.nochange[reliability] = 0
            for possibility, transitions in possibilities.iteritems():
                if possibility == "nocoordinators":
                    self.nochange[reliability] = transitions
                    continue
                self.transaway[reliability] += transitions
                s = []
                for group in possibility:
                    s.append( applymapping(group, peermap) )
                s.sort()
                self.transitions[ reliability ][ tuple(s) ] = transitions
                
    def gettimetoelection(self,probability):
        #print self.nochange
        try:
            total = self.nochange[probability] + self.transaway[probability]
            #No coordinators is a failure!!!
            failrate = (self.nochange[probability] * 1.0) / total
        except KeyError:
            return float("inf")
        try:
            return AYT_RATE / (1 - failrate)
        except ZeroDivisionError:
            return float("inf")
    
    def getelectiontransitions(self,probability):
        lm = {}
        if probability in self.transitions:
            for group in self.config:
                lm[ group.members[0] ] = group.members[1:]
            for config,transitions in self.transitions[probability].iteritems():
                cprime = []
                for group in config:
                    t = []
                    primeleader = group[0]
                    for m in group:
                        if m != primeleader:   
                            t.append(m)
                        t += lm[m]
                    t.sort()
                    t = [ primeleader ] + t
                    cprime.append( tuple(t) )
                cprime.sort()
                yield ( StatePool.getsystembytuple(tuple(cprime)), (transitions * 1.0) / self.transaway[probability] )
    
    def getgrouptransitions(self,probability):
        degrades = []
        configs = [ list(self.config) for _ in self.config ]
        i = 0
        for config in configs:
            group = config[i]
            lambd = group.getlambda(probability)
            for newgroup, occurance in group.gettransitions(probability):
                t = list(config)
                t[i] = newgroup
                yield ( make_state(t), lambd * occurance) 

    def astuple(self):
        return tuple([ g.members for g in self.config ])

    def assharpe(self):
        return tuptosharpe(self.astuple())

    def __repr__(self):
        return str(self.astuple())
        
    def __eq__(self, other):
        return self.config == other.config
    
    def __ne__(self, other):
        return self.config != other.config
    
    def __hash__(self):
        t = tuple([ g.members for g in self.config ])
        return t.__hash__()

def tuptosharpe(inp):
    s = ""
    return "_".join( [ "".join([ str(m) for m in group ]) for group in inp ])
        
def graphbuilder( roottuple, probability ):
    root = StatePool.getsystembytuple(roottuple)
    filename ="result{}.gv".format(probability) 
    filename2 = "markov{}.mk".format(probability)
    f = open(filename,'w')
    f.write("digraph markov_chain { \n")
    f.write("rankdir=LR;\n")
    s = open(filename2,'w')
    s.write("format 8\n")
    s.write("factor on\n")
    sharpedesc = "TRANS{}".format(probability) 
    s.write("markov {}\n".format(sharpedesc))
    openset = set( [ root ] )
    closedset = set()
    noelect = set()
    edgeout = {}
    edgein = {}
    electionset = set()
    while len(openset) > 0:
        current = openset.pop()
        print "Considering {}".format(current)
        if current in closedset:
            continue
        closedset.add(current)
        etime = current.gettimetoelection(probability)
        lmbd = 1.0/etime
        if lmbd > 0.0:
            sanity = 0
            for (config, occurance) in current.getelectiontransitions(probability):
                label = "{0:.3f} ({1:.2f}s)".format(occurance*lmbd, occurance*etime)
                f.write("\"{}\" -> \"{}E{}\" [ label = \"{}\" ]; \n".format(current,current,config,label))
                s.write("{} {}E{} {}\n".format(current.assharpe(), current.assharpe(), config.assharpe(), occurance*lmbd))
                sanity += occurance
                lmbd2 = (1.0 / ELECTION_DURATION)
                if lmbd2 == 0.0:
                    continue
                openset.add(config)
                try:
                    edgeout[current] += 1
                except KeyError:
                    edgeout[current] = 1
                try:
                    edgein[config] += 1
                except KeyError:
                    edgein[config] = 1
                t = 1.0 / lmbd2
                label = "{0:.3f} ({1:.2f}s)".format(lmbd2, t)
                f.write("\"{}E{}\" -> \"{}\" [label = \"{}\" ]; \n".format(current,config,config,label))
                s.write("{}E{} {} {}\n".format(current.assharpe(), config.assharpe(), config.assharpe(), lmbd2))
                electionset.add("{}E{}".format(current.assharpe(), config.assharpe()))
        else:
            noelect.add(current)
        for (config, lmbd) in current.getgrouptransitions(probability):
            if lmbd == 0.0:
                continue
            openset.add(config)
            try:
                edgeout[current] += 1
            except KeyError:
                edgeout[current] = 1
            try:
                edgein[config] += 1
            except KeyError:
                edgein[config] = 1
            t = 1/lmbd
            label = "{0:.3f} ({1:.2f}s)".format(lmbd, t)
            f.write("\"{}\" -> \"{}\" [ label = \"{}\" ]; \n".format(current,config,label))
            s.write("{} {} {}\n".format(current.assharpe(), config.assharpe(), lmbd))
    f.write("}\n")
    f.close()
    s.write("reward\n")
    bnd = []
    for sys in closedset:
        #if sys == root:
        #    continue
        shp = sys.assharpe()
        s.write("{} rew_{}\n".format(shp,shp))
        rwd = reward(sys.astuple())
        bnd.append( (shp,rwd) )
    for election in electionset:
        s.write("{} rew_{}\n".format(election,election))
        bnd.append( (election,0 ) )
    s.write("end\n")
    s.write("{} {}\n".format(root.assharpe(),1.0))
    s.write("end\n")
    s.write("bind\n")
    for shp, rew in bnd:
        s.write("rew_{} {}\n".format( shp, rew ) )
    s.write("end\n")
    s.write("var SS_trans cexrt(600;{})\n".format(sharpedesc))
    s.write("var SS_avail cexrt(60;{})\n".format(sharpedesc))
    s.write("var SS_rate exrt(60;{})\n".format(sharpedesc))
    s.write("expr SS_trans\n")
    s.write("expr SS_avail\n")
    s.write("expr SS_rate\n")
    s.write("end\n")
    s.close()
    for state in closedset:
        try:
            if edgein[state] >= 1 and edgeout[state] >= 1:
                continue
        except KeyError:
            pass
        print "State {} is reducible!".format(state)
    return filename
    
def reward(conftuple):
    return 1 if any( [ len(g) > 1 for g in conftuple ] ) else 0
    """
    rwd = 0
    for m in range(PARTICIPANTS):
        for g in conftuple:
            if m in g and len(g) > 1:
                rwd += .25
                break
    return rwd
    """
    #return sum( [ len(g) * 1.0 for g in conftuple ] ) / len(conftuple)

def test():
    # One! for each group configuration, make sure that it can be loaded from
    # the tuple:
    for group in groupgen.generate():
        print "Trying group: {}".format(group)
        StatePool.getgroupbytuple(group)
    
    print "All Groups Loaded Okay!"
    
    for system in groupgen.overviews():
        print "Trying system: {}".format(system)
        StatePool.getsystembytuple(system)
        
    print "All Systems Loaded Okay!"
    
def main(dotest=True):
    if dotest:
        test()
    for p in range(0,101,5):
        print "!!! RUNNING {}".format(p)
        resultfile = graphbuilder( ( (0,), (1,), (2,), (3,) ), p)
        subprocess.call(["dot", resultfile, "-oresult{}.png".format(p), "-Tpng:cairo", "-Kcirco"])

if __name__ == "__main__":
    main(False)
