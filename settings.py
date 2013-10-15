# This information gets loaded from a config file
import datetime
import json

import protocol

# 5 seconds for AYC
# 30 for premerge
# 5 for accepts
# 5 for readys
# 45 seconds total
# 225 @ 200ms, 450 @ 100ms


class Configuration(object):
    def __init__(self):    
        self.PARTICIPANTS = None
        self.PREMERGES = None
        self.OFFSETS = None
        self.PARTITIONS = None

        self.GRANULARITY = None
        self.PROTOCOL = None
        self.RESEND = None

        self.GLOBAL_TIMEOUT = None
        self.TIMEOUT_TIMEOUT = None
        self.CHECK_TIMEOUT = None

        self.ELECTION_TRIALS = None
        self.ELECTION_MAX_TICKS = None
        self.ELECTION_MAX_CHECKS = None

        self.AYC_TRIALS = None
        self.AYC_MAX_TICKS = None
        self.AYC_MAX_CHECKS = None

        self.PROFILE_FILE = None
        self.LOAD_DATE = None

        self.profile = None

    def save(self,filename):
        f = open(filename,'w')
        json.dump(self.profile,f,indent=4)
        f.close

    def clone(self,np=None):
        config = Configuration()
        newprof = dict(self.profile)
        if np:
            newprof["participants"] = sum(np)
            newprof["partitions"] = list(np)
        config.load_from_dict(newprof)
        return config

    def load_from_profile(self,filename):
        f = open(filename)
        profile = json.load(f)
        self.profile = profile
        self.load_from_dict(profile)

    def load_from_dict(self,profile):
        self.profile = dict(profile)

        self.PARTICIPANTS = profile["participants"]
        self.PREMERGES = profile["premerges"]
        self.OFFSETS = profile["offsets"]
        self.PARTITIONS = profile["partitions"]

        self.GRANULARITY = profile["granularity"]
        self.RESEND = profile["resend"]
        self.PROTOCOL = profile["protocol"]
        if self.PROTOCOL == "SUC":
            self.PROTOCOL = protocol.SUC
        elif self.PROTOCOL == "SRC":
            self.PROTOCOL = protocol.SRC
        else:
            print "Unrecognized protocol type"
            exit(1)

        self.GLOBAL_TIMEOUT = profile["global_timeout"] / self.RESEND
        self.TIMEOUT_TIMEOUT = profile["timeout_timeout"] / self.RESEND
        self.CHECK_TIMEOUT = profile["check_timeout"] / self.RESEND

        self.ELECTION_TRIALS = profile["election"]["trials"]
        self.ELECTION_MAX_TICKS = profile["election"]["max_time"] / self.RESEND
        self.ELECTION_MAX_CHECKS = profile["election"]["max_checks"]

        self.AYC_TRIALS = profile["ayc"]["trials"]
        self.AYC_MAX_TICKS = profile["ayc"]["max_time"] / self.RESEND
        self.AYC_MAX_CHECKS = profile["ayc"]["max_checks"]

        self.LOAD_DATE = datetime.datetime.today()

    def print_profile_summary(self):
        
        print "################# PROFILE SUMMARY ####################"
        print "## File: {}".format(self.PROFILE_FILE)
        print "## Loaded: {}".format(self.LOAD_DATE)
        print "##"
        print "## Participants: {}".format(self.PARTICIPANTS)
        print "## Premerges: {}".format(self.PREMERGES)
        print "## Offsets: {}".format(self.OFFSETS)
        print "##"
        print "## Granularity: {}".format(self.GRANULARITY)
        print "## Global Timeout: {}".format(self.GLOBAL_TIMEOUT)
        print "## Timeout Timeout: {}".format(self.TIMEOUT_TIMEOUT)
        print "## Check Timeout: {}".format(self.CHECK_TIMEOUT)
        print "##"
        print "## Election :: Trials: {}".format(self.ELECTION_TRIALS)
        print "## Election :: Max Ticks: {}".format(self.ELECTION_MAX_TICKS)
        print "## Election :: Max Checks: {}".format(self.ELECTION_MAX_CHECKS)
        print "##"
        print "## AYC :: Trials: {}".format(self.AYC_TRIALS)
        print "## AYC :: Max Ticks: {}".format(self.AYC_MAX_TICKS)
        print "## AYC :: Max Checks: {}".format(self.AYC_MAX_CHECKS)
        print "################# PROFILE SUMMARY ####################"

CONFIG = Configuration()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print "Give me an profile file as an argument and I will print a summary."
    else:
        CONFIG.load_from_profile(sys.argv[1])
        CONFIG.print_profile_summary() 
