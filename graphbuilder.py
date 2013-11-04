import json
import os

PARTITIONS = [2,2]
PARTICIPANTS = 4
SOURCE = "out"

def tupletofile(ftype, tup):
    tup = list(tup)
    return desctofile(ftype, [ str(x) for x in list(tup) ].join("-"))

def desctofile(ftype, desc):
    return "{}-{}.dat".format(ftype, desc )

def partitionmap():
    ptop = {}
    j = 0
    r = {}
    partitions = list(PARTITIONS)
    for i in range(PARTICIPANTS):
        while len(partitions) > 0 and partitions[0] == 0:
            j += 1
            partitions.pop(0)
        if len(partitions) > 0:
            partitions[0] -= 1
            ptop[i] = j
    return ptop

def converttof(tup):
    ptop = partitionmap()
    t = [ 0 for _ in range(len(ptop)) ]
    for i in tup:
        for j in i:
            t[ ptop[j] ] += 1
    # if the leader (first one) isn't in partition 0, rotate the list so the
    # leader's partition is first.
    t = t[tup[0]:] + t[:tup[0]]
    # TODO: sort the remainder to merge similiar states?
    return tuple(t)

def parsecommentedjson(fp):
    result = ""
    for line in fp:
        if str.find("##") != -1:
            result += line
    return json.reads(result)

def loadmapping(filename):
    d = {}
    f = open(filename)
    for l in f:
        tokens = l.split('\t')
        key = eval(tokens[0])
        #Token 1 the current view
        d[key] = {}
        #Token 2 the election set to load
        d[key]['set'] = tokens[1]
        #Token 3 the mapping to the new set
        c = 0  
        for v in eval(tokens[2]):
            d[key]['map'][c] = v
            c += 1
    return d

def remap(resultconfig, mapping):
    r = []
    for group in resultconfig:
        g = []
        for member in group:
            g.append(mapping[member])
        g = tuple( g[:1] + sorted(g[1:]) )
        r.append(g)
    return tuple(sorted(r))            
    
# Start with the root state because you can't degrade out of that.
openset = set()
openset.add( ((0), (1), (2), (3)) )

closedset = set()

graph = {}

AYTMAP = loadmapping('AYT-trans.tsv')
ELECTIONMAP = loadmapping('ELECTION-trans.tsv')

while len(openset) > 0:
    # For a state to be processed:
    current = openset.pop(0)
    closedset.add(current)

    # Consider if this state can degrade. If it can (leaders < PARTICIPANTS).
    # examine the AYC file to see how it degrades. Transition time is inversely
    # related to the time between AYCs and how many succeed. 
    if len(current) < PARTICIPANTS:
        #Extract each group from the current descriptor
        combined = {}
        for g in current:
            dset = AYTMAP[g]['set']
            dmap = AYTMAP[g]['map']
            if dset == None:
                continue
            fpath = os.path.join( SOURCE, desctofile('AYC',dmap) )
            f = open(fpath)
            dataset = parsecommentedjson(f)
            for prob in dataset:
                if prob not in combined:
                    combined[prob] = []
                #For each probablitiy in the dataset, see how it degrades.
                #Node 0 is always the leader. The new leader is the same as
                #old one, but more leaders could have been created.
                for resultconfig in dataset[prob]:
                    combined[prob] += remap(resultconfig, mapping)
        for prob in combined:
            if prob not in graph:
                graph[prob] = {}
            for resultconfig in combined[prob]:
                graph[prob][current] = (resultconfig,dataset[prob][resultconfig])
                if resultconfig not in closedset:
                    openset.add(resultconfig)
    else:
        #This state can't degrade.
        pass
    # Then, consider how long it takes to discover a new peer. This is an inverse
    # relation between the % of AYC's that succeed and the amount of time between
    # AYC checks (From the elction data) we transistions us to the related
    # reconfiguration state. If degrading is an option, use the appropriate
    # formula to determine what the expected time in state is.
    if len(current) > 1:
        #Map the leaders set to a election configuration file.
        #Translate the first of each group to be converted to a file to open.
        #Use those to make a reconfiguration vertex and then map it to the current
        #Group. make connections to other states.

    # Then, in the reconfiguration state after the fixed amount of time it takes
    # to perform an election transition to one of the several possible states as
    # prescribed by the results of the simulation (lambdas as % functions of the
    # count of transitions)

    # Then for each of the resulting states, add them to the graph and put them
    # in the processing queue, if they haven't been already.
