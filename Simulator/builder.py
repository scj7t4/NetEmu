#This builds a series of profiles from a base partition profile.
import os

from settings import *

def state_generator(root):
    if len(root) == 0:
        yield []
    else:
        t = list(root)
        f = t.pop(0)
        for i in range(f+1):
            q = [i]
            for sub in state_generator(t):
                tmp = q + sub
                #print tmp
                yield tmp

UTILITIES = [('AYC',"aycmulti.py"), ('ELECTION',"electionmulti.py"), ('INVITE',"invitemulti.py")]

def main():
    import sys
    if len(sys.argv) != 2:
        print "Give me a profile as an argument"
    else:
        CONFIG.load_from_profile(sys.argv[1])
        CONFIG.print_profile_summary()

    f = open('buildout.sh','w')    

    for generated in state_generator([2,2]):
        print generated
        newconfig = CONFIG.clone(generated)
        root,ext = os.path.splitext(sys.argv[1])
        descriptor = "-"+"-".join([str(x) for x in generated])
        nfn = root+descriptor+ext
        newconfig.save(nfn)
        f.write("mkdir -p out\n")
        for util in UTILITIES:
            f.write("python2 {} {} > out/{}{}.dat\n".format(util[1],nfn,util[0],descriptor))
    
    f.close()

if __name__ == "__main__":
    main()
