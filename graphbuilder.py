import json
import os

PARTITIONS = [2,2]
PARTICIPANTS = 4
SOURCE = "out"

def tupletofile(ftype, tup):
    tup = list(tup)
    return "{}-{}.dat".format(ftype, [ str(x) for x in list(tup) ].join("-") )

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

def buildmapping(group,aycmapping):
    c = 0
    d = {}
    seen = set()
    leader = group[0]
    #build a reverse map
    ptop = partitionmap()
    rtop = {}
    for k in ptop:
        try:
            rtop[ ptop[k] ].append(k)
        except KeyError:
            rtop[ ptop[k] ] = [k]

    for i in range(len(group)):
        if i in seen:
            continue
        d[c] = i
        c += 1
        seen.add(i)
        part = ptop[i]
        others = rtop[part]
        for x in others:
            if x in group and not seen(x):
                d[c] = x
                c += 1
                seen.add(x)
    return d

def remap(aycconfig, mapping)
    r = []
    for g in aycconfig:
        r.append( tuple([ mapping[m] for m in g ]) )
    return tuple(r)
            
       

# Start with the root state because you can't degrade out of that.
openset = set()
openset.add( ((0), (1), (2), (3)) )

closedset = set()

graph = {}

while len(openset) > 0:
    # For a state to be processed:
    current = openset.pop(0)
    closedset.add(current)

    # Consider if this state can degrade. If it can (leaders < PARTICIPANTS).
    # examine the AYC file to see how it degrades. Transition time is inversely
    # related to the time between AYCs and how many succeed. 
    if len(current) < participants:
        #Extract each group from the current descriptor
        for g in current:
            if len(g) > 1:
                #We convert the current descriptor to a file descriptor:
                fdesc = converttof(g)
                #The convert that to a filename:
                fpath = os.path.join( source, tupletofile('AYC',fdec) )
                f = open(fpath)
                dataset = parsecommentedjson(f)
                mapping = buildmapping(g, fdesc)
                for prob in dataset:
                    #For each probablitiy in the dataset, see how it degrades.
                    #Node 0 is always the leader. The new leader is the same as
                    #old one, but more leaders could have been created.
                    if prob not in graph:
                        graph[prob] = {}
                    for resultconfig in dataset[prob]:
                        resultconfig = remap(resultconfig, mapping)
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
