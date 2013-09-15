
def avg(ds):
    return sum(ds)*1.0 / len(ds)

def median(ds):
    if len(ds) == 1:
        return ds[0]
    if len(ds) == 0:
        return None
    ds.sort()
    k = len(ds)/2
    q = len(ds)/2 % 1
    m = avg([ds[k], ds[k+q]])
    return m

def quartiles(ds):
    d = median(ds)
    q1 = median([ x for x in ds if x < d ])
    q3 = median([ x for x in ds if x >= d ])
    if q1 == None:
        q1 = d
    if q3 == None:
        q3 = d
    return [ min(ds), q1, d, q3, max(ds) ]

def stats_set(ds):
    a = avg(ds)
    variance = avg( [ (x - a)*(x - a) for x in ds ] )
    q = quartiles(ds)
    return [a,variance] + q


