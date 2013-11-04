import random

def attempt_delivery(p):
    if random.random() <= p/100.0:
        return True
    return False

class SUC(object):
    def __init__(self,reliability):
        self.q = []
        self.ACK = None
        self.s = 0
        self.p = reliability

    def tick(self):
        i = 0
        while i < len(self.q) and i < 8:
            if attempt_delivery(self.p):
                yield ('MSG',self.q[i][0],self.q[i][1])
            i += 1
        if self.ACK != None and attempt_delivery(self.p):
            yield ('ACK',self.ACK,'')
            #self.ACK = None

    def recv(self, msg):
        (t,s,m) = msg
        if t == 'ACK':
            while 0 < len(self.q) and self.q[0][0] <= s:
                self.q.pop(0)
            return True
        if t == 'MSG' and (self.ACK == None or self.ACK < s):
            self.ACK = s
            return True
        return False
            
    def send(self, msg):
        self.q.append((self.s,msg))
        self.s += 1

class SRC(object):
    def __init__(self,reliability):
        self.q = []
        self.ACK = None
        self.s = 0
        self.p = reliability

    def tick(self,p):
        if len(self.q) > 0 and attempt_delivery(self.p):
            yield ('MSG',self.q[0][0],self.q[0][1])
        if self.ACK != None and attempt_delivery(self.p):
            yield ('ACK',self.ACK,'')

    def recv(self,msg):
        (t,s,m) = msg
        if t == 'ACK':
            if len(self.q) > 0 and self.q[0][0] == s:
                self.q.pop(0)
            return True
        if t == 'MSG' and (self.ACK == None or self.ACK+1 == s):
            self.ACK = s
            return True
        return False
    
    def send(self, msg):
        self.q.append((self.s,msg))
        self.s += 1
