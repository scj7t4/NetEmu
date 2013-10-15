#This builds a series of profiles from a base partition profile.

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

def main():
    import sys
    if len(sys.argv) != 2:
        print "Give me a profile as an argument"
    else:
        CONFIG.load_from_profile(sys.argv[1])
        CONFIG.print_profile_summary

    for generated in state_generator([2,2]):
        print generated
        newconfig = CONFIG.clone(generated)
        nfn = sys.argv[1].replace(".","-"+"-".join([str(x) for x in generated])+".")
        newconfig.save(nfn)

if __name__ == "__main__":
    main()
